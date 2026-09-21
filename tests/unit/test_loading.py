import json

import pytest

from zimmteb.datasets.registry import load_dataset


def test_external_manifest_cannot_escape_root(tmp_path, tiny):
    folder = tmp_path / "datasets" / "manifests"
    folder.mkdir(parents=True)
    manifest = tiny.manifest.model_dump(mode="json")
    manifest["documents"] = "../../private.jsonl"
    path = folder / "invalid.yaml"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="escapes dataset root"):
        load_dataset(str(path))


def test_unknown_dataset_rejected():
    with pytest.raises(ValueError, match="Expected one manifest"):
        load_dataset("does-not-exist")
