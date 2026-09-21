"""Offline review packets bound to exact dataset bytes and record content."""

import hashlib
import json
from datetime import date
from typing import Any, Literal

from pydantic import Field

from zimmteb.config import StrictModel, registry
from zimmteb.datasets.registry import RetrievalDataset
from zimmteb.datasets.schema import Document, Query
from zimmteb.datasets.validation import ValidationReport, validate


class SourceEntry(StrictModel):
    source_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    license: str = Field(min_length=1)
    license_evidence: str = Field(min_length=1)
    permission_scope: str = Field(min_length=1)
    approved_by: str = Field(min_length=1)
    approval_date: date
    redistribution_allowed: Literal[True]


class SourceCatalog(StrictModel):
    sources: list[SourceEntry] = []


class ReviewDecision(StrictModel):
    reviewer_id: str = Field(min_length=1)
    review_date: date
    status: Literal["approved", "needs-revision", "rejected"]
    languages_reviewed: list[str] = Field(min_length=1)
    comments: str = Field(min_length=1)
    privacy_checked: bool
    judgments_checked: bool = False


class ReviewItem(StrictModel):
    record_type: Literal["document", "query"]
    record_id: str
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    record: dict[str, Any]
    decision: ReviewDecision | None = None


class ReviewPacket(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    dataset_id: str
    dataset_version: str
    dataset_checksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    items: list[ReviewItem]


def record_key(record: Document | Query) -> tuple[Literal["document", "query"], str]:
    return (
        ("document", record.document_id) if isinstance(record, Document) else ("query", record.id)
    )


def content_hash(value: dict[str, Any]) -> str:
    content = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def export_packet(data: RetrievalDataset) -> ReviewPacket:
    validation = validate(data)
    if not validation.valid:
        raise ValueError("Cannot export invalid data: " + "; ".join(validation.errors))
    items = []
    all_records: list[Document | Query] = [*data.documents, *data.queries]
    for record in all_records:
        kind, id_ = record_key(record)
        value = record.model_dump(mode="json")
        items.append(
            ReviewItem(
                record_type=kind, record_id=id_, content_sha256=content_hash(value), record=value
            )
        )
    return ReviewPacket(
        dataset_id=data.manifest.dataset_id,
        dataset_version=data.manifest.version,
        dataset_checksum=data.actual_checksum,
        items=items,
    )


def check_packet(
    data: RetrievalDataset, packet: ReviewPacket, catalog: SourceCatalog
) -> ValidationReport:
    """Validate supplied attestations, never infer that human work actually occurred."""
    report = validate(data)
    if (packet.dataset_id, packet.dataset_version, packet.dataset_checksum) != (
        data.manifest.dataset_id,
        data.manifest.version,
        data.actual_checksum,
    ):
        report.errors.append("Review packet is bound to a different dataset/version/checksum")
    sources = {source.source_id: source for source in catalog.sources}
    if len(sources) != len(catalog.sources):
        report.errors.append("Duplicate source catalog IDs")
    all_records: list[Document | Query] = [*data.documents, *data.queries]
    records = {record_key(r): r for r in all_records}
    seen = set()
    languages = registry("languages")
    for item in packet.items:
        key = (item.record_type, item.record_id)
        label = "/".join(key)
        if key in seen:
            report.errors.append(f"{label}: duplicate review item")
        seen.add(key)
        record = records.get(key)
        if record is None:
            report.errors.append(f"{label}: unknown review target")
            continue
        expected = record.model_dump(mode="json")
        if item.content_sha256 != content_hash(expected) or item.record != expected:
            report.errors.append(
                f"{label}: stale or edited review content; correct source and re-export"
            )
        source = sources.get(record.source_id or "")
        if source is None:
            report.errors.append(f"{label}: no approved source catalog entry")
        elif source.license != record.license or source.source != record.source:
            report.errors.append(f"{label}: source/license differs from approval evidence")
        elif source.approval_date > date.today():
            report.errors.append(f"{label}: source approval is future-dated")
        if not record.source_document_id or not record.translation_family_id:
            report.errors.append(f"{label}: source-document and translation-family IDs required")
        decision = item.decision
        if decision is None or decision.status != "approved":
            report.errors.append(f"{label}: human approval pending")
            continue
        if decision.review_date > date.today():
            report.errors.append(f"{label}: human review is future-dated")
        if not decision.privacy_checked:
            report.errors.append(f"{label}: privacy review pending")
        code = record.language if isinstance(record, Document) else record.query_language
        language = languages.get(code)
        required = set(language.code_switch_partners or [code]) if language else {code}
        source_language = record.metadata.get("source_language")
        if record.metadata.get("translation_method") not in {None, "none"} and source_language:
            required.add(source_language)
        if not required <= set(decision.languages_reviewed):
            report.errors.append(f"{label}: bilingual/language review coverage incomplete")
        if set(decision.languages_reviewed) - languages.keys():
            report.errors.append(f"{label}: unknown language in review coverage")
        if isinstance(record, Query) and not decision.judgments_checked:
            report.errors.append(f"{label}: relevance judgments need review")
    for key in sorted(records.keys() - seen):
        report.errors.append(f"{'/'.join(key)}: missing review item")
    report.warnings.append(
        "This checks recorded attestations, not reviewer identity or legal/linguistic correctness; "
        "it does not publish data or change canonical review status."
    )
    return report
