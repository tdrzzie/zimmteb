import json

import pytest
from typer.testing import CliRunner

from zimmteb.cli import app
from zimmteb.reporting import compare
from zimmteb.results import RunConfig, read_result
from zimmteb.runner import run_benchmark


def test_mteb_pipeline_cache_resume_and_slices(tmp_path):
    output, cache = tmp_path / "run", tmp_path / "cache"
    config = RunConfig(model="test-hash")
    result = run_benchmark(config, output, cache)
    restored = read_result(output)
    assert result == restored
    native = json.loads((output / "mteb-results.json").read_text())
    assert native["task_results"][0]["task_name"] == "ZimMTEBTinyRetrieval"
    overall = next(s for s in result.slices if s.dimension == "overall")
    native_scores = native["task_results"][0]["scores"]["test"][0]
    assert overall.metrics["ndcg_at_10"] == pytest.approx(native_scores["ndcg_at_10"], abs=1e-5)
    assert {s.value for s in result.slices if s.dimension == "query_language"} == {
        "eng",
        "sna",
        "nde",
        "eng-sna-codeswitch",
        "eng-nde-codeswitch",
    }
    assert run_benchmark(config, output, cache, resume=True).run_id == result.run_id
    cached = run_benchmark(config, tmp_path / "cached", cache)
    assert set(cached.efficiency["cache_hits"]) == {"query", "document"}
    with pytest.raises(ValueError, match="already has a result"):
        run_benchmark(config.model_copy(update={"seed": 7}), output, resume=True)
    assert "Synthetic infrastructure measurements" in (output / "report.md").read_text()
    runner = CliRunner()
    validation = runner.invoke(app, ["results", "validate", "--run", str(output)])
    assert validation.exit_code == 0, validation.output


def test_filters_keep_full_corpus_and_comparison_guard(tmp_path):
    result = run_benchmark(
        RunConfig(model="test-hash", language="sna", domain="agriculture"), tmp_path / "sliced"
    )
    assert len(result.queries) == 1
    assert result.queries[0].query_language == "sna"
    assert result.efficiency["corpus_documents"] == 16
    assert compare(result, result)["delta_right_minus_left"] == 0
    different = result.model_copy(update={"dataset_checksum": "0" * 64})
    with pytest.raises(ValueError, match="Incompatible"):
        compare(result, different)


def test_empty_filter_fails_before_model_load(tmp_path):
    with pytest.raises(ValueError, match="No queries"):
        run_benchmark(
            RunConfig(model="test-hash", language="nde", domain="financial-services"), tmp_path
        )


@pytest.mark.parametrize(
    "command",
    [
        ["--help"],
        ["languages", "list"],
        ["domains", "list"],
        ["models", "list"],
        ["datasets", "list"],
        ["benchmark", "list"],
    ],
)
def test_cli_discovery(command):
    result = CliRunner().invoke(app, command)
    assert result.exit_code == 0, result.output


def test_cli_validation_output(tmp_path):
    result = CliRunner().invoke(app, ["datasets", "validate", "--output", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert json.loads((tmp_path / "validation.json").read_text())["valid"]


@pytest.mark.network
def test_real_cpu_model(tmp_path):
    result = run_benchmark(RunConfig(), tmp_path / "real")
    assert result.model_metadata["parameter_count"] > 0


@pytest.mark.gpu
def test_real_cuda_model(tmp_path):
    result = run_benchmark(RunConfig(device="cuda"), tmp_path / "cuda")
    assert result.efficiency["peak_cuda_allocated_bytes"] > 0
