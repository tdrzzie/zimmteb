import pytest
from pydantic import ValidationError

from zimmteb.datasets.schema import Manifest
from zimmteb.hardware import select_device
from zimmteb.results import QueryResult


def test_manifest_rejects_absolute_paths(tiny):
    manifest = tiny.manifest.model_dump()
    for path in ("C:\\secret.jsonl", "/etc/passwd", "C:relative-drive.jsonl"):
        manifest["documents"] = path
        with pytest.raises(ValidationError):
            Manifest.model_validate(manifest)


def test_result_rejects_bad_scores():
    from zimmteb.metrics import ranking_metrics

    value = dict(
        query_id="q",
        query_language="eng",
        document_languages=["eng"],
        domain="education",
        code_switch=False,
        ranking=["a"],
        relevance_scores=[1.0],
        positive_document_ids=["a"],
        metrics=ranking_metrics(["a"], {"a": 1.0}),
        failures=[],
    )
    assert QueryResult.model_validate(value)
    value["metrics"]["ndcg_at_10"] = float("nan")
    with pytest.raises(ValidationError):
        QueryResult.model_validate(value)


def test_device_fallback_is_explicit(monkeypatch):
    import torch

    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    assert select_device("auto") == "cpu"
    with pytest.raises(ValueError, match="CUDA requested"):
        select_device("cuda")
