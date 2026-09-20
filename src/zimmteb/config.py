"""Validated configuration, loaded identically from a checkout or installed wheel."""

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)


class Language(StrictModel):
    code: str
    name: str
    alternate_names: list[str] = []
    scripts: list[str]
    tokenizer_considerations: str
    benchmark_availability: str
    notes: str
    code_switch_partners: list[str] = []


class Domain(StrictModel):
    code: str
    name: str
    description: str


class ModelConfig(StrictModel):
    # Whitespace is semantically significant in model prompts.
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    id: str
    adapter: Literal["sentence-transformers", "test-hash", "sonar"]
    model_name: str
    revision: str
    license: str
    license_url: str
    query_prefix: str = ""
    document_prefix: str = ""
    normalize: bool = True
    max_length: int = Field(default=128, ge=8)
    batch_size: int = Field(default=8, ge=1)
    precision: Literal["float32"] = "float32"
    trust_remote_code: Literal[False] = False
    notes: str = ""


def resource_root() -> Path:
    packaged = Path(__file__).parent / "resources"
    return packaged if packaged.exists() else Path(__file__).resolve().parents[2]


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return data


def registry(kind: str) -> dict[str, Any]:
    schemas: dict[str, type[StrictModel]] = {
        "languages": Language, "domains": Domain, "models": ModelConfig
    }
    schema = schemas[kind]
    result = {}
    for path in sorted((resource_root() / "configs" / kind).glob("*.yaml")):
        item = schema.model_validate(read_yaml(path))
        key = getattr(item, "code", getattr(item, "id", None))
        if key in result:
            raise ValueError(f"Duplicate {kind} ID: {key}")
        result[key] = item
    return result


def model_config(name: str) -> ModelConfig:
    path = Path(name)
    if path.is_file():
        return ModelConfig.model_validate(read_yaml(path))
    models = registry("models")
    if name not in models:
        raise ValueError(f"Unknown model {name!r}; use models list")
    return models[name]  # type: ignore[no-any-return]
