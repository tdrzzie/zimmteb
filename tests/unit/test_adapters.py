import numpy as np

from zimmteb.config import model_config
from zimmteb.models.adapters import HashTestAdapter, SentenceTransformerAdapter


class SpyModel:
    def __init__(self):
        self.calls = []

    def encode_query(self, texts, **kwargs):
        self.calls.append(("query", texts, kwargs))
        return np.ones((len(texts), 3))

    def encode_document(self, texts, **kwargs):
        self.calls.append(("document", texts, kwargs))
        return np.ones((len(texts), 3))


def test_asymmetric_prompts_and_options():
    adapter = SentenceTransformerAdapter(model_config("multilingual-e5-small"))
    spy = SpyModel()
    adapter.model = spy
    assert adapter.encode_queries(["query"]).shape == (1, 3)
    adapter.encode_documents(["passage"])
    assert spy.calls[0][0] == "query"
    assert spy.calls[0][2]["prompt"] == "query: "
    assert spy.calls[1][2]["prompt"] == "passage: "
    assert spy.calls[0][2]["normalize_embeddings"] is True
    adapter.close()
    assert adapter.model is None


def test_hash_repeatability():
    model = HashTestAdapter(model_config("test-hash"))
    a = model.encode_queries(["maize garden water"])
    np.testing.assert_array_equal(a, model.encode_documents(["maize garden water"]))
    np.testing.assert_allclose(np.linalg.norm(a), 1.0, rtol=1e-6)


def test_local_model_disk_measurement(tmp_path):
    (tmp_path / "config.json").write_bytes(b"{}")
    (tmp_path / "weights").mkdir()
    (tmp_path / "weights" / "example.dat").write_bytes(b"12345")
    config = model_config("multilingual-e5-small").model_copy(update={"model_name": str(tmp_path)})
    assert SentenceTransformerAdapter(config).metadata()["model_disk_bytes"] == 7
