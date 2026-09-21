"""ZimMTEB CLI. Model downloads occur only during an explicitly requested run."""

import functools
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer
from pydantic import ValidationError

from zimmteb.config import read_yaml, registry, resource_root
from zimmteb.datasets.registry import load_dataset, manifests
from zimmteb.datasets.schema import Manifest
from zimmteb.datasets.validation import ValidationReport, validate
from zimmteb.results import RunConfig, read_result, write_json

app = typer.Typer(no_args_is_help=True, help="Zimbabwe Multilingual Text Embedding Benchmark")
groups = {
    name: typer.Typer(no_args_is_help=True)
    for name in (
        "system",
        "languages",
        "domains",
        "datasets",
        "models",
        "benchmark",
        "results",
        "report",
        "failures",
    )
}
for name, group in groups.items():
    app.add_typer(group, name=name)


def handled(function: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except typer.Exit:
            raise
        except (ValueError, OSError, RuntimeError) as error:
            typer.echo(f"Error: {error}", err=True)
            raise typer.Exit(1) from error

    return wrapper


def emit(value: Any) -> None:
    typer.echo(json.dumps(value, ensure_ascii=False, indent=2, default=str, allow_nan=False))


@groups["system"].command("info")
@handled
def info(output: Path | None = None) -> None:
    from zimmteb.hardware import system_info

    value = system_info()
    if output:
        write_json(output, value)
    emit(value)


@groups["languages"].command("list")
def languages_list() -> None:
    emit([item.model_dump() for item in registry("languages").values()])


@groups["domains"].command("list")
def domains_list() -> None:
    emit([item.model_dump() for item in registry("domains").values()])


@groups["models"].command("list")
def models_list() -> None:
    emit([item.model_dump() for item in registry("models").values()])


@groups["datasets"].command("list")
@handled
def datasets_list() -> None:
    emit([Manifest.model_validate(read_yaml(path)).model_dump(mode="json") for path in manifests()])


@groups["datasets"].command("validate")
@handled
def datasets_validate(
    dataset: str = "tiny-synthetic", output: Path = Path("reports/validation")
) -> None:
    try:
        result = validate(load_dataset(dataset))
    except (ValidationError, ValueError, OSError) as error:
        result = ValidationReport(errors=[str(error)])
    output.mkdir(parents=True, exist_ok=True)
    value = {"valid": result.valid, **result.model_dump()}
    write_json(output / "validation.json", value)
    (output / "validation.md").write_text(result.markdown(), encoding="utf-8")
    emit(value)
    if not result.valid:
        raise typer.Exit(1)


@groups["benchmark"].command("list")
def benchmark_list() -> None:
    emit([read_yaml(path) for path in (resource_root() / "configs" / "benchmarks").glob("*.yaml")])


@groups["datasets"].command("review-export")
@handled
def review_export(
    dataset: str = "tiny-synthetic", output: Path = Path(".cache/curation/review.json")
) -> None:
    from zimmteb.datasets.curation import export_packet

    if output.exists():
        raise ValueError("Review output already exists; use a fresh path to preserve decisions")
    packet = export_packet(load_dataset(dataset))
    write_json(output, packet.model_dump(mode="json"))
    emit({"packet": str(output.resolve()), "records": len(packet.items), "status": "unreviewed"})


@groups["datasets"].command("review-check")
@handled
def review_check(
    packet: Path = typer.Option(...),
    sources: Path = typer.Option(...),
    dataset: str = "tiny-synthetic",
    output: Path = Path(".cache/curation/check.json"),
) -> None:
    from zimmteb.datasets.curation import ReviewPacket, SourceCatalog, check_packet

    if output.resolve() in {packet.resolve(), sources.resolve()}:
        raise ValueError("Review check output must not overwrite its inputs")
    result = check_packet(
        load_dataset(dataset),
        ReviewPacket.model_validate_json(packet.read_text(encoding="utf-8")),
        SourceCatalog.model_validate(read_yaml(sources)),
    )
    value = {"valid": result.valid, **result.model_dump()}
    write_json(output, value)
    emit(value)
    if not result.valid:
        raise typer.Exit(1)


@groups["benchmark"].command("run")
@handled
def benchmark_run(
    config: Path | None = None,
    model: str | None = None,
    dataset: str | None = None,
    language: str | None = None,
    document_language: str | None = None,
    domain: str | None = None,
    task: str | None = None,
    device: str | None = None,
    batch_size: int | None = None,
    precision: str | None = None,
    seed: int | None = None,
    output: Path = Path("runs/first-benchmark"),
    cache: Path | None = None,
    resume: bool = False,
) -> None:
    from zimmteb.runner import run_benchmark

    values = read_yaml(config) if config else {}
    overrides = {
        "model": model,
        "dataset": dataset,
        "language": language,
        "document_language": document_language,
        "domain": domain,
        "task": task,
        "device": device,
        "batch_size": batch_size,
        "precision": precision,
        "seed": seed,
    }
    values.update({key: value for key, value in overrides.items() if value is not None})
    result = run_benchmark(RunConfig.model_validate(values), output, cache, resume)
    emit(
        {
            "run_id": result.run_id,
            "result": str((output / "result.json").resolve()),
            "report": str((output / "report.md").resolve()),
            "synthetic": result.synthetic,
        }
    )


@groups["benchmark"].command("compare")
@handled
def benchmark_compare(left: Path = typer.Option(...), right: Path = typer.Option(...)) -> None:
    from zimmteb.reporting import compare

    emit(compare(read_result(left), read_result(right)))


@groups["results"].command("validate")
@handled
def results_validate(run: Path = typer.Option(...)) -> None:
    from zimmteb.metrics import ranking_metrics, slices

    result = read_result(run)
    for query in result.queries:
        metrics = ranking_metrics(
            query.positive_document_ids,
            dict(zip(query.ranking, query.relevance_scores, strict=True)),
        )
        if any(abs(metrics[key] - query.metrics[key]) > 1e-8 for key in metrics):
            raise ValueError(f"Inconsistent metrics for {query.query_id}")
    if slices(result.queries) != result.slices:
        raise ValueError("Result slices do not match per-query metrics")
    emit({"valid": True, "run_id": result.run_id})


@groups["report"].command("generate")
@handled
def report_generate(
    run: Path = typer.Option(...), output: Path = Path("reports/benchmark.md")
) -> None:
    from zimmteb.reporting import generate_report

    generate_report(read_result(run), output)
    typer.echo(str(output.resolve()))


@groups["failures"].command("inspect")
@handled
def failures_inspect(run: Path = typer.Option(...)) -> None:
    result = read_result(run)
    emit([query.model_dump() for query in result.queries if query.failures])


if __name__ == "__main__":
    app()
