from datetime import date
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from zimmteb.config import StrictModel

ReviewStatus = Literal[
    "unreviewed", "machine-checked", "human-reviewed", "approved", "rejected", "needs-revision"
]


class Review(StrictModel):
    reviewer_id: str = Field(min_length=1)
    review_date: date
    revision: str = Field(min_length=1)
    status: ReviewStatus
    comments: str
    corrected_text: str | None = None
    previous_version: str


class CodeSwitch(StrictModel):
    primary_language: str
    secondary_language: str
    switch_frequency: int = Field(ge=1)
    estimated_switch_ratio: float = Field(gt=0, lt=1)
    switch_direction: str
    origin: Literal["natural", "human-created", "translated", "synthetic"]
    human_reviewed: bool = False

    @model_validator(mode="after")
    def distinct_languages(self) -> "CodeSwitch":
        if self.primary_language == self.secondary_language:
            raise ValueError("Code-switch languages must differ")
        if self.switch_direction != f"{self.primary_language}->{self.secondary_language}":
            raise ValueError("Switch direction must match primary->secondary")
        return self


class Provenance(StrictModel):
    source: str = Field(min_length=1)
    license: str = Field(min_length=1)
    synthetic: bool
    human_review_status: ReviewStatus
    metadata: dict[str, Any] = {}
    reviews: list[Review] = []
    source_id: str | None = Field(default=None, min_length=1)
    source_document_id: str | None = Field(default=None, min_length=1)
    translation_family_id: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def require_evidence(self) -> "Provenance":
        if self.synthetic:
            required = {
                "generator",
                "generator_version",
                "generation_parameters",
                "source_language",
                "translation_method",
            }
            if not required <= self.metadata.keys():
                raise ValueError(f"Synthetic provenance requires {sorted(required)}")
        if self.human_review_status in {"human-reviewed", "approved"} and not self.reviews:
            raise ValueError("Human review claims require review records")
        return self


class Document(Provenance):
    document_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    title: str = ""
    language: str = Field(min_length=1)
    domain: str = Field(min_length=1)


class Query(Provenance):
    id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    query_language: str = Field(min_length=1)
    positive_document_ids: list[str] = Field(min_length=1)
    hard_negative_document_ids: list[str] = []
    negative_document_ids: list[str] = []
    domain: str = Field(min_length=1)
    difficulty: Literal["easy", "medium", "hard", "unknown"] = "unknown"
    split: Literal["train", "dev", "test"] = "test"
    code_switch: CodeSwitch | None = None

    @model_validator(mode="after")
    def disjoint_judgments(self) -> "Query":
        positives = set(self.positive_document_ids)
        if len(positives) != len(self.positive_document_ids):
            raise ValueError("Duplicate positive IDs")
        if positives & set(self.hard_negative_document_ids + self.negative_document_ids):
            raise ValueError("Positive document is also a negative")
        return self


class Manifest(StrictModel):
    dataset_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    languages: list[str] = Field(min_length=1)
    task: Literal["retrieval"]
    domains: list[str] = Field(min_length=1)
    splits: dict[str, int]
    license: str = Field(min_length=1)
    citation: str = Field(min_length=1)
    source: str = Field(min_length=1)
    creation_method: str = Field(min_length=1)
    human_review_level: ReviewStatus
    number_of_samples: int = Field(gt=0)
    checksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    creation_date: date
    benchmark_version: str
    documents: str
    queries: str

    @field_validator("documents", "queries")
    @classmethod
    def safe_relative_file(cls, value: str) -> str:
        from pathlib import PurePosixPath, PureWindowsPath

        if (
            PureWindowsPath(value).drive
            or PureWindowsPath(value).root
            or PurePosixPath(value).is_absolute()
        ):
            raise ValueError("Dataset paths must be relative")
        return value
