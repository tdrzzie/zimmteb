import numpy as np
import pytest

from zimmteb.cache import EmbeddingCache, content_key
from zimmteb.metrics import paired_bootstrap, ranking_metrics


def test_known_ranking_multiple_positives():
    scores = ranking_metrics(["a", "c"], {"b": 3.0, "a": 2.0, "c": 1.0})
    assert scores["recall_at_1"] == 0
    assert scores["recall_at_5"] == 1
    assert scores["mrr_at_10"] == 0.5
    assert scores["map_at_10"] == pytest.approx((0.5 + 2 / 3) / 2)
    assert scores["ndcg_at_10"] == pytest.approx(
        (1 / np.log2(3) + 1 / np.log2(4)) / (1 + 1 / np.log2(3))
    )


def test_ties_and_unretrieved_relevance():
    scores = ranking_metrics(["a", "missing"], {"a": 1.0, "z": 1.0})
    assert scores["mrr_at_10"] == 0.5
    assert scores["recall_at_20"] == 0.5


def test_cache_roundtrip_and_corruption(tmp_path):
    cache = EmbeddingCache(tmp_path)
    key = content_key({"model": "x", "revision": "1", "prompt": "q:"})
    values = np.ones((2, 3), dtype=np.float32)
    cache.put(key, values)
    np.testing.assert_array_equal(cache.get(key, 2), values)
    assert cache.get(key, 3) is None
    (tmp_path / f"{key}.npz").write_bytes(b"corrupt")
    assert cache.get(key, 2) is None


@pytest.mark.parametrize(
    "field", ["revision", "checksum", "prompt", "precision", "split", "normalize", "seed"]
)
def test_cache_identity_invalidation(field):
    a = {
        "revision": "a",
        "checksum": "b",
        "prompt": "q:",
        "precision": "float32",
        "split": "test",
        "normalize": True,
        "seed": 42,
    }
    b = dict(a)
    b[field] = "changed"
    assert content_key(a) != content_key(b)


def test_bootstrap_aligned_deterministic():
    a = paired_bootstrap([0, 0.5, 1], [0.5, 1, 1])
    assert a == paired_bootstrap([0, 0.5, 1], [0.5, 1, 1])
    assert a["delta_right_minus_left"] == pytest.approx(1 / 3)
    assert paired_bootstrap([1, 1], [1, 1])["ci95_low"] == 0
