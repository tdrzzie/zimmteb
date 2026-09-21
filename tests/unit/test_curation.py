from datetime import date

import pytest
from typer.testing import CliRunner

from zimmteb.cli import app
from zimmteb.datasets.curation import (
    ReviewDecision,
    SourceCatalog,
    SourceEntry,
    check_packet,
    export_packet,
)
from zimmteb.datasets.validation import validate


def prepared(tiny):
    # Test-only attestations, never exported as real approvals.
    for i, record in enumerate([*tiny.documents, *tiny.queries]):
        record.source_id = "test-source"
        record.source_document_id = f"test-page-{i}"
        record.translation_family_id = f"test-family-{i}"
    catalog = SourceCatalog(
        sources=[
            SourceEntry(
                source_id="test-source",
                source=tiny.queries[0].source,
                license=tiny.manifest.license,
                license_evidence="test-only evidence",
                permission_scope="test-only text redistribution",
                approved_by="test-only-owner",
                approval_date=date(2020, 1, 1),
                redistribution_allowed=True,
            )
        ]
    )
    packet = export_packet(tiny)
    for item in packet.items:
        item.decision = ReviewDecision(
            reviewer_id="test-only-reviewer",
            review_date=date(2020, 1, 1),
            status="approved",
            languages_reviewed=["eng", "sna", "nde"],
            comments="Test-only approval; no human review occurred.",
            privacy_checked=True,
            judgments_checked=True,
        )
    return packet, catalog


def test_export_does_not_invent_approval(tiny):
    packet = export_packet(tiny)
    assert len(packet.items) == 29
    assert all(item.decision is None for item in packet.items)
    report = check_packet(tiny, packet, SourceCatalog())
    assert not report.valid
    assert any("human approval pending" in e for e in report.errors)


def test_complete_test_attestations_are_checked_without_changing_source(tiny):
    packet, catalog = prepared(tiny)
    report = check_packet(tiny, packet, catalog)
    assert report.valid, report.errors
    assert tiny.queries[0].human_review_status == "unreviewed"
    assert tiny.queries[0].synthetic


@pytest.mark.parametrize(
    "change", ["text", "judgment", "packet", "checksum", "missing", "duplicate"]
)
def test_review_binding_rejects_stale_or_incomplete_evidence(tiny, change):
    packet, catalog = prepared(tiny)
    if change == "text":
        tiny.documents[0].text += " Another sentence."
    elif change == "judgment":
        tiny.queries[0].positive_document_ids = [tiny.documents[-1].document_id]
    elif change == "packet":
        packet.items[0].record["text"] = "Tampered packet content"
    elif change == "checksum":
        packet.dataset_checksum = "0" * 64
    elif change == "missing":
        packet.items.pop()
    else:
        packet.items.append(packet.items[0])
    assert not check_packet(tiny, packet, catalog).valid


def test_review_checks_language_privacy_and_judgments(tiny):
    packet, catalog = prepared(tiny)
    query = next(i for i in packet.items if i.record.get("code_switch"))
    query.decision.languages_reviewed = ["eng"]
    query.decision.privacy_checked = False
    query.decision.judgments_checked = False
    errors = check_packet(tiny, packet, catalog).errors
    assert any("coverage incomplete" in e for e in errors)
    assert any("privacy review" in e for e in errors)
    assert any("judgments need review" in e for e in errors)


def test_source_evidence_and_review_date(tiny):
    packet, catalog = prepared(tiny)
    catalog.sources[0].license = "different-license"
    packet.items[0].decision.review_date = date(2999, 1, 1)
    errors = check_packet(tiny, packet, catalog).errors
    assert any("source/license differs" in e for e in errors)
    assert any("future-dated" in e for e in errors)


def test_cross_language_judgments_require_document_language_review(tiny):
    query = tiny.queries[0]
    query.positive_document_ids = [
        next(d.document_id for d in tiny.documents if d.language == "sna")
    ]
    query.negative_document_ids = []
    query.hard_negative_document_ids = []
    packet, catalog = prepared(tiny)
    item = next(i for i in packet.items if i.record_type == "query" and i.record_id == query.id)
    item.decision.languages_reviewed = ["eng"]
    assert any("coverage incomplete" in e for e in check_packet(tiny, packet, catalog).errors)
    item.decision.languages_reviewed = ["eng", "sna"]
    assert check_packet(tiny, packet, catalog).valid


def test_translation_family_leakage_without_lexical_overlap(tiny):
    left, right = tiny.queries[:2]
    left.split = "train"
    left.translation_family_id = right.translation_family_id = "shared-family"
    assert any("translation/shared-family" in e for e in validate(tiny).errors)


def test_negative_document_source_leakage(tiny):
    tiny.queries[0].split = "train"
    first = tiny.documents[0]
    first.source_id = "source"
    first.source_document_id = "page"
    target = tiny.documents[-1]
    target.source_id = "source"
    target.source_document_id = "page"
    tiny.queries[1].negative_document_ids = [target.document_id]
    assert any("source/source/page" in e for e in validate(tiny).errors)


def test_review_cli_preserves_existing_packet_and_reports_pending(tmp_path):
    runner = CliRunner()
    packet = tmp_path / "packet.json"
    assert runner.invoke(app, ["datasets", "review-export", "--output", str(packet)]).exit_code == 0
    original = packet.read_bytes()
    assert runner.invoke(app, ["datasets", "review-export", "--output", str(packet)]).exit_code == 1
    assert packet.read_bytes() == original
    catalog = tmp_path / "sources.yaml"
    catalog.write_text("sources: []", encoding="utf-8")
    output = tmp_path / "check.json"
    result = runner.invoke(
        app,
        [
            "datasets",
            "review-check",
            "--packet",
            str(packet),
            "--sources",
            str(catalog),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 1
    assert output.exists()
    assert "human approval pending" in result.output
    assert "Error: 1" not in result.output
