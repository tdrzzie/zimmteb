import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from zimmteb.config import read_yaml, resource_root
from zimmteb.datasets.schema import Document, Manifest, Query


@dataclass
class RetrievalDataset:
    manifest: Manifest
    documents: list[Document]
    queries: list[Query]
    actual_checksum: str


def manifests() -> list[Path]:
    return sorted((resource_root() / "datasets" / "manifests").glob("*.yaml"))


def checksum(documents: bytes, queries: bytes) -> str:
    # Length framing prevents ambiguous concatenation.
    digest = hashlib.sha256()
    for content in (documents, queries):
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def load_dataset(name: str = "tiny-synthetic") -> RetrievalDataset:
    path = Path(name)
    if not path.is_file():
        matches = [p for p in manifests() if read_yaml(p).get("dataset_id") == name]
        if len(matches) != 1:
            raise ValueError(f"Expected one manifest for {name!r}, found {len(matches)}")
        path = matches[0]
    manifest = Manifest.model_validate(read_yaml(path))
    root = path.resolve().parent.parent

    def read(relative: str) -> bytes:
        target = (path.parent / relative).resolve()
        if not target.is_relative_to(root):
            raise ValueError("Dataset file escapes dataset root")
        return target.read_bytes()

    docs, queries = read(manifest.documents), read(manifest.queries)
    return RetrievalDataset(
        manifest,
        [Document.model_validate(json.loads(line)) for line in docs.decode("utf-8").splitlines() if line.strip()],
        [Query.model_validate(json.loads(line)) for line in queries.decode("utf-8").splitlines() if line.strip()],
        checksum(docs, queries),
    )
