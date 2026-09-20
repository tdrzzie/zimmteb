"""Per-query audit metrics backed by the same trec_eval engine used by MTEB."""

from collections import defaultdict

import numpy as np
import pytrec_eval

from zimmteb.results import QueryResult, SliceResult

METRICS = ["recall_at_1", "recall_at_5", "recall_at_10", "recall_at_20", "mrr_at_10", "ndcg_at_10", "map_at_10"]


def ranking_metrics(positives: list[str], scores: dict[str, float]) -> dict[str, float]:
    if not positives or not scores:
        raise ValueError("Metrics require positives and at least one ranked document")
    if not all(np.isfinite(value) for value in scores.values()):
        raise ValueError("Non-finite retrieval scores")
    judgments = {"q": {id_: 1 for id_ in positives}}
    evaluator = pytrec_eval.RelevanceEvaluator(judgments, {"recall.1,5,10,20", "ndcg_cut.10", "map_cut.10"})
    raw = evaluator.evaluate({"q": scores})["q"]
    # trec_eval breaks equal scores by descending document ID; match explicitly.
    ranking = sorted(scores, key=lambda id_: (scores[id_], id_), reverse=True)
    reciprocal = next((1 / rank for rank, id_ in enumerate(ranking[:10], 1) if id_ in positives), 0.0)
    return {**{f"recall_at_{k}": raw[f"recall_{k}"] for k in (1, 5, 10, 20)},
            "mrr_at_10": reciprocal, "ndcg_at_10": raw["ndcg_cut_10"], "map_at_10": raw["map_cut_10"]}


def slices(queries: list[QueryResult]) -> list[SliceResult]:
    groups: dict[tuple[str, str], list[QueryResult]] = defaultdict(list)
    for query in queries:
        dimensions = [("overall", "all"), ("query_language", query.query_language),
                      ("domain", query.domain), ("task", "retrieval"),
                      ("code_switch", query.query_language if query.code_switch else "monolingual"),
                      ("language_domain", f"{query.query_language}/{query.domain}"),
                      ("language_pair", f"{query.query_language}->{','.join(query.document_languages)}")]
        for key in dimensions:
            groups[key].append(query)
    return [SliceResult(dimension=dimension, value=value, count=len(items),
                        metrics={metric: float(np.mean([q.metrics[metric] for q in items])) for metric in METRICS})
            for (dimension, value), items in sorted(groups.items())]


def paired_bootstrap(left: list[float], right: list[float], seed: int = 42, repetitions: int = 2000) -> dict[str, float]:
    if not left or len(left) != len(right):
        raise ValueError("Paired bootstrap requires aligned, nonempty observations")
    difference = np.asarray(right) - np.asarray(left)
    rng = np.random.default_rng(seed)
    draws = np.array([rng.choice(difference, len(difference), replace=True).mean() for _ in range(repetitions)])
    low, high = np.quantile(draws, [0.025, 0.975])
    return {"delta_right_minus_left": float(difference.mean()), "ci95_low": float(low), "ci95_high": float(high)}
