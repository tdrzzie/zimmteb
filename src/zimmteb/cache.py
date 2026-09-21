"""Content-addressed numeric-only cache; untrusted pickle is never loaded."""

import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import numpy as np

from zimmteb.models.adapters import Embeddings


def content_key(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")
    ).hexdigest()


def check_embeddings(values: Embeddings, rows: int) -> None:
    if values.ndim != 2 or values.shape[0] != rows or values.shape[1] == 0:
        raise ValueError("Invalid embedding shape")
    if not np.isfinite(values).all():
        raise ValueError("Non-finite embeddings")


class EmbeddingCache:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def get(self, key: str, rows: int) -> Embeddings | None:
        path = self.directory / f"{key}.npz"
        if not path.exists():
            return None
        try:
            with np.load(path, allow_pickle=False) as stored:
                values = np.asarray(stored["embeddings"], dtype=np.float32)
                if str(stored["checksum"].item()) != hashlib.sha256(values.tobytes()).hexdigest():
                    return None
                check_embeddings(values, rows)
                return values
        except (ValueError, OSError, KeyError, EOFError, zipfile.BadZipFile):
            return None

    def put(self, key: str, values: Embeddings) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        check_embeddings(values, len(values))
        fd, temporary = tempfile.mkstemp(dir=self.directory, suffix=".npz")
        try:
            with os.fdopen(fd, "wb") as stream:
                np.savez_compressed(
                    stream, embeddings=values, checksum=hashlib.sha256(values.tobytes()).hexdigest()
                )
            os.replace(temporary, self.directory / f"{key}.npz")
        finally:
            Path(temporary).unlink(missing_ok=True)
