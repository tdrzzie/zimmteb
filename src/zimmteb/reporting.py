import json
from pathlib import Path

from zimmteb.config import registry
from zimmteb.metrics import paired_bootstrap
from zimmteb.results import RunResult


def markdown_report(result: RunResult) -> str:
    lines = [
        "# ZimMTEB retrieval report",
        "",
        f"Run: `{result.run_id}`",
        "",
        f"Model: `{result.model.model_name}` @ `{result.model.revision}`",
        "",
        f"Dataset: `{result.dataset_id}` {result.dataset_version}; benchmark {result.benchmark_version}",
        f"Checksum: `{result.dataset_checksum}`",
        "",
        "**Synthetic infrastructure measurements only. No linguistic validity or model superiority is established.**"
        if result.synthetic
        else "Review dataset governance before interpreting scores.",
        "",
        "Scores are query macro-averages on a shared corpus; unjudged documents count as nonrelevant.",
        "Other-language equivalents may be false negatives in this tiny fixture.",
        "",
        "| Slice | Value | Queries | Recall@1 | Recall@5 | Recall@10 | Recall@20 | MRR@10 | nDCG@10 | MAP@10 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    order = {"overall": 0, "query_language": 1, "code_switch": 2, "domain": 3}
    metrics = (
        "recall_at_1",
        "recall_at_5",
        "recall_at_10",
        "recall_at_20",
        "mrr_at_10",
        "ndcg_at_10",
        "map_at_10",
    )
    for item in sorted(
        result.slices, key=lambda s: (order.get(s.dimension, 4), s.dimension, s.value)
    ):
        values = " | ".join(f"{item.metrics[m]:.4f}" for m in metrics)
        lines.append(f"| {item.dimension} | {item.value} | {item.count} | {values} |")
    for dimension, kind in (("query_language", "languages"), ("domain", "domains")):
        present = {s.value for s in result.slices if s.dimension == dimension}
        missing = sorted(set(registry(kind)) - present)
        if missing:
            lines.extend(
                [
                    "",
                    f"Not evaluated ({dimension}): {', '.join(missing)}. These are missing values, not zero scores.",
                ]
            )
    lines.extend(
        [
            "",
            "## Efficiency",
            "",
            "Indexing and query phases are measured separately. Cached runs measure cache reads, not inference speed.",
            "Batch query timing is not single-request latency. RSS peak is sampled; CUDA peak is allocator memory.",
            "",
            "```json",
            json.dumps(result.efficiency, indent=2),
            "```",
            "",
            "## Failures",
            "",
        ]
    )
    failed = [q for q in result.queries if q.failures]
    lines.extend(
        f"- `{q.query_id}` ({q.query_language}, {q.domain}): {', '.join(q.failures)}; top result `{q.ranking[0]}`"
        for q in failed
    )
    if not failed:
        lines.append("No automatically detected top-1 failures on this fixture.")
    lines.extend(
        [
            "",
            "These labels are mechanical ranking observations; lexical traps and semantic causes require human analysis.",
            "",
            "## Reproducibility",
            "",
            f"Git commit: `{result.environment.get('git_commit')}`; dirty: `{result.environment.get('git_dirty')}`.",
            f"Seed: {result.config.seed}; review level: {result.human_review_status}.",
            "Native MTEB results and the manifest accompany this report. No task or score was submitted upstream.",
            "",
            "## Limitations",
            "",
            *[f"- {warning}" for warning in result.warnings],
            "- This dataset is too small and unreviewed for significance claims.",
            "- No trained zim-embed-small or zim-reranker is supplied.",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_report(result: RunResult, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown_report(result), encoding="utf-8")


def compare(left: RunResult, right: RunResult) -> dict[str, object]:
    for field in (
        "benchmark_version",
        "dataset_id",
        "dataset_version",
        "dataset_checksum",
        "evaluation_engine",
    ):
        if getattr(left, field) != getattr(right, field):
            raise ValueError(f"Incompatible results: {field} differs")
    if left.config.split != right.config.split:
        raise ValueError("Incompatible evaluation splits")
    a, b = {q.query_id: q for q in left.queries}, {q.query_id: q for q in right.queries}
    if a.keys() != b.keys():
        raise ValueError("Paired comparisons require exactly the same query IDs")
    ids = sorted(a)
    return {
        "metric": "ndcg_at_10",
        "queries": len(ids),
        **paired_bootstrap(
            [a[id_].metrics["ndcg_at_10"] for id_ in ids],
            [b[id_].metrics["ndcg_at_10"] for id_ in ids],
        ),
        "warning": "Illustrative paired query bootstrap; correlated queries and tiny synthetic data do not support scientific claims.",
    }
