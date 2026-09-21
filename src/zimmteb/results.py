import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, model_validator

from zimmteb.config import ModelConfig, StrictModel


class RunConfig(StrictModel):
    name: str = "ZimMTEBTinyRetrieval"
    version: str = "0.1.0"
    dataset: str = "tiny-synthetic"
    task: Literal["retrieval"] = "retrieval"
    model: str = "multilingual-e5-small"
    device: Literal["cpu", "cuda", "auto"] = "cpu"
    batch_size: int = Field(default=8, ge=1)
    precision: Literal["float32"] = "float32"
    seed: int = Field(default=42, ge=0)
    split: Literal["train", "dev", "test"] = "test"
    language: str | None = None
    document_language: str | None = None
    domain: str | None = None


class QueryResult(StrictModel):
    query_id: str
    query_language: str
    document_languages: list[str]
    domain: str
    code_switch: bool
    metrics: dict[str, float]
    ranking: list[str]
    relevance_scores: list[float]
    positive_document_ids: list[str]
    failures: list[str]

    @model_validator(mode="after")
    def valid_ranking(self) -> "QueryResult":
        if len(self.ranking) != len(self.relevance_scores) or len(set(self.ranking)) != len(
            self.ranking
        ):
            raise ValueError("Ranking IDs/scores must align and be unique")
        required = {
            "recall_at_1",
            "recall_at_5",
            "recall_at_10",
            "recall_at_20",
            "mrr_at_10",
            "ndcg_at_10",
            "map_at_10",
        }
        if self.metrics.keys() != required or any(
            not 0 <= value <= 1 for value in self.metrics.values()
        ):
            raise ValueError("Ranking metrics must be finite values in [0, 1]")
        if not self.ranking or not self.positive_document_ids:
            raise ValueError("Ranking and positive judgments must not be empty")
        return self


class SliceResult(StrictModel):
    dimension: str
    value: str
    count: int = Field(gt=0)
    metrics: dict[str, float]


class RunResult(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    run_id: str
    timestamp: datetime
    identity: str = Field(pattern=r"^[0-9a-f]{64}$")
    benchmark_version: str
    config: RunConfig
    dataset_id: str
    dataset_version: str
    dataset_checksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    model: ModelConfig
    model_metadata: dict[str, Any]
    environment: dict[str, Any]
    synthetic: bool
    human_review_status: str
    evaluation_engine: Literal["mteb"] = "mteb"
    efficiency: dict[str, Any]
    runtime_seconds: float = Field(ge=0)
    queries: list[QueryResult] = Field(min_length=1)
    slices: list[SliceResult] = Field(min_length=1)
    warnings: list[str] = []

    @model_validator(mode="after")
    def unique_queries(self) -> "RunResult":
        if len({q.query_id for q in self.queries}) != len(self.queries):
            raise ValueError("Duplicate query results")
        return self


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    fd, temp = tempfile.mkstemp(dir=path.parent, suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


def read_result(path: Path) -> RunResult:
    if path.is_dir():
        path = path / "result.json"
    return RunResult.model_validate_json(path.read_text(encoding="utf-8"))
