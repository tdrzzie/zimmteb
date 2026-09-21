"""Regenerate immutable v0.1 synthetic fixture bytes; run from a source checkout.

Text below is AI-drafted infrastructure data, NOT authenticated translations.
Change dataset and benchmark versions before releasing any changed fixture.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate() -> None:
    # Each tuple is an independently drafted query/document, not parallel gold bitext.
    samples = {
        "eng": [
            (
                "How can I check my mobile wallet balance?",
                "Open the wallet menu and select balance enquiry.",
                "mobile-payments",
            ),
            (
                "When should I water my vegetable garden?",
                "Water vegetables early in the morning to reduce evaporation.",
                "agriculture",
            ),
            (
                "How do I reset my internet router?",
                "Restart the router by switching its power off and on.",
                "technology-support",
            ),
        ],
        "sna": [
            (
                "Ndingatarisa sei mari iri mufoni mangu?",
                "Vhura menyu yemari pafoni wosarudza kutarisa mari yasara.",
                "mobile-payments",
            ),
            (
                "Ndinofanira kudiridza muriwo rinhi?",
                "Diridza muriwo mangwanani kuti mvura isakurumidza kuoma.",
                "agriculture",
            ),
            (
                "Ndingabhadhara sei mari yechikoro?",
                "Bvunza kuhofisi yechikoro nzira dzekubhadhara mari.",
                "education",
            ),
        ],
        "nde": [
            (
                "Ngingakhangela njani imali esele efonini yami?",
                "Vula imenyu yemali efonini ukhethe ukukhangela imali esele.",
                "mobile-payments",
            ),
            (
                "Kumele ngithelele imibhida nini?",
                "Thelela imibhida ekuseni ukuze amanzi angaphangisi ukoma.",
                "agriculture",
            ),
            (
                "Ngingabhadala njani imali yesikolo?",
                "Buza ehofisini yesikolo ngezindlela zokubhadala imali.",
                "education",
            ),
        ],
        "eng-sna-codeswitch": [
            (
                "My wallet transfer failed, ndingadzorera sei mari yangu?",
                "Kana transfer yaramba, check the transaction reference wobata customer support.",
                "customer-support",
            ),
            (
                "The maize leaves are drying, ndingadiridza kangani?",
                "Tarisa hunyoro hwevhu before watering the maize again.",
                "agriculture",
            ),
        ],
        "eng-nde-codeswitch": [
            (
                "My wallet transfer failed, ngingayithola njani imali yami?",
                "Nxa transfer ingaphumelelanga, check the reference ubikele customer support.",
                "customer-support",
            ),
            (
                "The maize leaves are drying, ngithelele kangaki?",
                "Khangela ubumanzi bomhlabathi before watering the maize again.",
                "agriculture",
            ),
        ],
    }
    docs, queries = [], []
    for language, records in samples.items():
        for index, (query, text, domain) in enumerate(records):
            key = f"{language}-{index}"
            provenance = {
                "source": "original AI-drafted ZimMTEB infrastructure fixture",
                "license": "CC0-1.0",
                "synthetic": True,
                "human_review_status": "unreviewed",
                "metadata": {
                    "generator": "codex-authored-static-fixture",
                    "generator_version": "0.1.0",
                    "generation_parameters": {"purpose": "pipeline-smoke-test", "template": key},
                    "source_language": language,
                    "translation_method": "none",
                },
            }
            docs.append(
                {
                    "document_id": f"d-{key}",
                    "text": text,
                    "title": "",
                    "language": language,
                    "domain": domain,
                    **provenance,
                }
            )
            item = {
                "id": f"q-{key}",
                "query": query,
                "query_language": language,
                "positive_document_ids": [f"d-{key}"],
                "hard_negative_document_ids": [],
                "negative_document_ids": [],
                "domain": domain,
                "difficulty": "unknown",
                "split": "test",
                **provenance,
            }
            if "codeswitch" in language:
                partner = language.split("-")[1]
                item["code_switch"] = {
                    "primary_language": "eng",
                    "secondary_language": partner,
                    "switch_frequency": 1,
                    "estimated_switch_ratio": 0.5,
                    "switch_direction": f"eng->{partner}",
                    "origin": "synthetic",
                    "human_reviewed": False,
                }
                item["metadata"]["generation_parameters"]["switch_estimates"] = (
                    "rough author estimates, not token annotated"
                )
            queries.append(item)
    # Distinct distractors test ranking beyond paired answer memorization.
    for i, (text, domain) in enumerate(
        [
            ("A savings account statement lists deposits and withdrawals.", "financial-services"),
            (
                "A mobile data bundle provides internet access for a fixed period.",
                "telecommunications",
            ),
            ("Public library opening hours are displayed at the entrance.", "public-information"),
        ]
    ):
        docs.append(
            {
                "document_id": f"d-distractor-{i}",
                "text": text,
                "title": "",
                "language": "eng",
                "domain": domain,
                "source": "original AI-drafted ZimMTEB infrastructure fixture",
                "license": "CC0-1.0",
                "synthetic": True,
                "human_review_status": "unreviewed",
                "metadata": {
                    "generator": "codex-authored-static-fixture",
                    "generator_version": "0.1.0",
                    "generation_parameters": {"purpose": "distractor"},
                    "source_language": "eng",
                    "translation_method": "none",
                },
            }
        )
    contents = []
    target = ROOT / "datasets" / "tiny-synthetic"
    target.mkdir(parents=True, exist_ok=True)
    for filename, records in (("documents.jsonl", docs), ("queries.jsonl", queries)):
        content = "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records
        ).encode("utf-8")
        (target / filename).write_bytes(content)
        contents.append(content)
    digest = hashlib.sha256()
    for content in contents:
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    # JSON is also valid YAML, avoiding a bootstrap dependency.
    manifest = {
        "dataset_id": "tiny-synthetic",
        "version": "0.1.0",
        "languages": list(samples),
        "task": "retrieval",
        "domains": sorted({d["domain"] for d in docs}),
        "splits": {"test": len(queries)},
        "license": "CC0-1.0",
        "citation": "ZimMTEB contributors, synthetic infrastructure fixture v0.1.0",
        "source": "original AI-drafted fixture; no external dataset incorporated",
        "creation_method": "synthetic",
        "human_review_level": "unreviewed",
        "number_of_samples": len(queries),
        "checksum": digest.hexdigest(),
        "creation_date": "2026-09-20",
        "benchmark_version": "0.1.0",
        "documents": "../tiny-synthetic/documents.jsonl",
        "queries": "../tiny-synthetic/queries.jsonl",
    }
    path = ROOT / "datasets" / "manifests" / "tiny-synthetic.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    generate()
