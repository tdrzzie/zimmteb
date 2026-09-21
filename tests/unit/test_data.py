import copy

import pytest
from pydantic import ValidationError

from zimmteb.config import ModelConfig, model_config, registry
from zimmteb.datasets.registry import checksum
from zimmteb.datasets.schema import Query
from zimmteb.datasets.validation import validate


def test_registries_and_pins():
    languages = registry("languages")
    assert set(languages) == {"eng", "sna", "nde", "eng-sna-codeswitch", "eng-nde-codeswitch"}
    assert languages["nde"].name == "isiNdebele (Northern Ndebele)"
    assert len(registry("domains")) == 8
    assert len(model_config("multilingual-e5-small").revision) == 40
    assert model_config("multilingual-e5-small").query_prefix == "query: "


def test_valid_fixture(tiny):
    assert len(tiny.queries) == 13
    assert len(tiny.documents) == 16
    report = validate(tiny)
    assert report.valid, report.errors
    assert report.warnings


def test_checksum_is_byte_sensitive_and_framed():
    assert checksum(b"ab", b"c") != checksum(b"a", b"bc")
    assert checksum(b"a\n", b"b") != checksum(b"a\r\n", b"b")


@pytest.mark.parametrize(
    "field,value", [("query", "  "), ("source", ""), ("license", ""), ("positive_document_ids", [])]
)
def test_required_fields(tiny, field, value):
    data = tiny.queries[0].model_dump()
    data[field] = value
    with pytest.raises(ValidationError):
        Query.model_validate(data)


def test_positive_negative_overlap(tiny):
    data = tiny.queries[0].model_dump()
    data["hard_negative_document_ids"] = data["positive_document_ids"]
    with pytest.raises(ValidationError, match="also a negative"):
        Query.model_validate(data)


def test_review_claim_requires_record(tiny):
    data = tiny.queries[0].model_dump()
    data["human_review_status"] = "approved"
    with pytest.raises(ValidationError, match="review records"):
        Query.model_validate(data)


def test_synthetic_provenance_required(tiny):
    data = tiny.queries[0].model_dump()
    data["metadata"] = {}
    with pytest.raises(ValidationError, match="Synthetic provenance"):
        Query.model_validate(data)


def test_duplicate_checks(tiny):
    tiny.queries.append(tiny.queries[0])
    tiny.documents.append(tiny.documents[0])
    errors = validate(tiny).errors
    assert any("Duplicate query ID" in error for error in errors)
    assert any("Duplicate document text" in error for error in errors)


def test_cross_split_leakage(tiny):
    other = copy.deepcopy(tiny.queries[0])
    other.id = "new-id"
    other.split = "train"
    other.query += "!"
    tiny.queries.append(other)
    assert any("Cross-split query leakage" in error for error in validate(tiny).errors)


def test_checksum_dangling_and_language_errors(tiny):
    tiny.actual_checksum = "0" * 64
    tiny.queries[0].positive_document_ids = ["missing"]
    tiny.queries[0].query_language = "nbl"
    errors = validate(tiny).errors
    assert any("checksum mismatch" in error for error in errors)
    assert any("dangling" in error for error in errors)
    assert any("language" in error for error in errors)


def test_codeswitch_mismatch(tiny):
    query = next(q for q in tiny.queries if q.code_switch)
    query.code_switch.secondary_language = "zul"
    assert any("invalid code-switch language pair" in error for error in validate(tiny).errors)


def test_unicode_and_outliers(tiny):
    tiny.documents[0].text = "broken \ufffd text"
    tiny.queries[0].query = "x"
    report = validate(tiny)
    assert any("Unicode" in error for error in report.errors)
    assert any("extremely short" in warning for warning in report.warnings)


def test_remote_code_not_silent():
    data = model_config("multilingual-e5-small").model_dump()
    data["trust_remote_code"] = True
    with pytest.raises(ValidationError):
        ModelConfig.model_validate(data)
