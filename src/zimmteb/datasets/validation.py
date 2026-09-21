"""Deterministic structural checks; heuristics never certify linguistic validity."""

import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from typing import cast

from zimmteb.config import StrictModel, registry
from zimmteb.datasets.registry import RetrievalDataset
from zimmteb.datasets.schema import Document, Query


class ValidationReport(StrictModel):
    errors: list[str] = []
    warnings: list[str] = []

    @property
    def valid(self) -> bool:
        return not self.errors

    def markdown(self) -> str:
        lines = ["# Dataset validation", f"\nValid: {self.valid}"]
        for label, items in (("Errors", self.errors), ("Warnings", self.warnings)):
            lines.extend([f"\n## {label}\n", *[f"- {item}" for item in items]])
        return "\n".join(lines) + "\n"


def normalized(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def validate(dataset: RetrievalDataset) -> ValidationReport:
    report = ValidationReport()
    manifest = dataset.manifest
    languages, domains = registry("languages"), registry("domains")
    if dataset.actual_checksum != manifest.checksum:
        report.errors.append("Dataset checksum mismatch")
    if len(dataset.queries) != manifest.number_of_samples:
        report.errors.append("Query count differs from manifest")
    if dict(Counter(q.split for q in dataset.queries)) != manifest.splits:
        report.errors.append("Split counts differ from manifest")
    if set(manifest.languages) - languages.keys() or set(manifest.domains) - domains.keys():
        report.errors.append("Manifest contains unknown languages or domains")
    docs = {d.document_id: d for d in dataset.documents}
    # All judgments can expose source content during training, including negatives.
    group_splits: dict[tuple[str, ...], set[str]] = {}
    for query in dataset.queries:
        records_in_query: list[Document | Query] = [query]
        for id_ in (
            query.positive_document_ids
            + query.negative_document_ids
            + query.hard_negative_document_ids
        ):
            if id_ in docs:
                records_in_query.append(docs[id_])
                group_splits.setdefault(("document", id_), set()).add(query.split)
        for item in records_in_query:
            if item.source_document_id:
                key = ("source", item.source_id or item.source, item.source_document_id)
                group_splits.setdefault(key, set()).add(query.split)
            if item.translation_family_id:
                translation_key = ("translation", item.translation_family_id)
                group_splits.setdefault(translation_key, set()).add(query.split)
    for group, splits_used in sorted(group_splits.items()):
        if len(splits_used) > 1:
            report.errors.append(
                f"Cross-split source-family leakage: {'/'.join(group)} in {sorted(splits_used)}"
            )
    for kind, records, ids, texts in (
        (
            "document",
            dataset.documents,
            [d.document_id for d in dataset.documents],
            [d.text for d in dataset.documents],
        ),
        (
            "query",
            dataset.queries,
            [q.id for q in dataset.queries],
            [q.query for q in dataset.queries],
        ),
    ):
        for value, count in Counter(ids).items():
            if count > 1:
                report.errors.append(f"Duplicate {kind} ID: {value}")
        for value, count in Counter(map(normalized, texts)).items():
            if count > 1:
                report.errors.append(f"Duplicate {kind} text: {value[:60]}")
        for record, id_, text in zip(records, ids, texts, strict=True):
            language = getattr(record, "language", getattr(record, "query_language", ""))
            if language not in languages or language not in manifest.languages:
                report.errors.append(f"{id_}: unknown or undeclared language {language}")
            record_domain = cast(Document | Query, record).domain
            if record_domain not in domains or record_domain not in manifest.domains:
                report.errors.append(f"{id_}: unknown or undeclared domain")
            if record.license != manifest.license:
                report.errors.append(
                    f"{id_}: license differs from manifest; split licenses explicitly"
                )
            if any(unicodedata.category(c) in {"Cs", "Co"} or c == "\ufffd" for c in text):
                report.errors.append(f"{id_}: malformed/suspicious Unicode")
            if any(unicodedata.category(c) == "Cc" and c not in "\n\t\r" for c in text):
                report.errors.append(f"{id_}: control character")
            if len(text) < 8 or len(text.split()) < 2:
                report.warnings.append(f"{id_}: extremely short text")
            if len(text) > 20000:
                report.warnings.append(f"{id_}: extreme length outlier")
            if record.metadata.get("translation_method") not in {None, "none"}:
                report.warnings.append(f"{id_}: translation requires bilingual review")
    for query in dataset.queries:
        referenced = (
            query.positive_document_ids
            + query.negative_document_ids
            + query.hard_negative_document_ids
        )
        if set(referenced) - docs.keys():
            report.errors.append(f"{query.id}: dangling document references")
        language = languages.get(query.query_language)
        partners = language.code_switch_partners if language else []
        cs = query.code_switch
        if bool(partners) != bool(cs):
            report.errors.append(f"{query.id}: code-switch metadata presence mismatch")
        if cs and set(partners) != {cs.primary_language, cs.secondary_language}:
            report.errors.append(f"{query.id}: invalid code-switch language pair")
        if cs and cs.human_reviewed and not query.reviews:
            report.errors.append(f"{query.id}: code-switch review claim lacks evidence")
    # Tiny Phase 1 data: quadratic audit. Replace with candidate indexing for large corpora.
    for i, left in enumerate(dataset.queries):
        for right in dataset.queries[i + 1 :]:
            if left.split == right.split:
                continue
            similarity = SequenceMatcher(
                None, normalized(left.query), normalized(right.query)
            ).ratio()
            if similarity >= 0.9:
                report.errors.append(f"Cross-split query leakage: {left.id}/{right.id}")
            if set(left.positive_document_ids) & set(right.positive_document_ids):
                report.errors.append(f"Cross-split positive document overlap: {left.id}/{right.id}")
            for a in left.positive_document_ids:
                for b in right.positive_document_ids:
                    if (
                        a != b
                        and a in docs
                        and b in docs
                        and SequenceMatcher(
                            None, normalized(docs[a].text), normalized(docs[b].text)
                        ).ratio()
                        >= 0.9
                    ):
                        report.errors.append(f"Cross-split near-duplicate documents: {a}/{b}")
    if any(q.synthetic for q in dataset.queries):
        report.warnings.append(
            "Synthetic infrastructure fixture; not evidence of language competence"
        )
    if any(q.human_review_status == "unreviewed" for q in dataset.queries):
        report.warnings.append("Unreviewed text; linguistic validity is not established")
    return report
