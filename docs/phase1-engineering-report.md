# Phase 1 engineering report

Verified locally on Windows 11, Python 3.12.14, on 21 September 2026.
Phase 1 delivers retrieval infrastructure. The data is synthetic, AI-drafted and
unreviewed; the measured scores establish that the pipeline runs, not language
competence or model superiority. Nothing was published to a registry or leaderboard.

## Architecture and ownership

The pipeline is validation → local MTEB retrieval task → neutral model adapter →
document/query encoding → exact dense search → native MTEB evaluation → versioned
results → sliced reports and failure inspection.

MTEB 2.21.0 provides `AbsTaskRetrieval`, `TaskMetadata`, `Benchmark`, the search
protocol, evaluation orchestration, retrieval metrics, predictions and native result
serialization. The local task retains manifest-derived metadata when unloading;
upstream's default unloading assumes class-level published metadata.

Sentence Transformers 6.1.0 provides checkpoint loading, query/document encoding,
explicit prompts, batching, normalization and device execution. The implementation
uses its current `get_embedding_dimension` API. No upstream project is forked.

ZimMTEB adds five language tracks, eight domain definitions, provenance and review
schemas, checksum validation, duplicate/leakage checks, model configurations,
content-addressed embedding caches, reproducible run identities, resource sampling,
per-query audits, slicing, comparison guards, reporting and a CLI. Per-query metrics
use the same pytrec_eval backend as MTEB; MRR is independently checked on ranked IDs.

## Repository map

| Location | Purpose |
|---|---|
| `src/zimmteb/` | Typed implementation and CLI |
| `configs/` | Language, domain, model, benchmark and hardware registries |
| `datasets/` | Versioned 13-query/16-document fixture and manifests |
| `tests/` | Unit, offline integration, opt-in real-model and GPU checks |
| `docs/` | Methodology, upstream research, training design and 12 ADRs |
| `hf_templates/` | Dataset and future model card templates |
| `scripts/` | Deterministic fixture generator and tracked-artifact checks |
| `.github/workflows/` | Linux/Windows, Python 3.11/3.12 quality workflow |
| `reports/cpu-smoke/` | Measured CPU run, native results, manifest and predictions |

## Verification evidence

- Installation with development dependencies succeeded; frozen uv synchronization
  succeeded and `pip check` found no broken requirements.
- Source distribution and wheel build successfully. The wheel was installed into a
  separate folder, imported outside the source checkout, and its bundled 13-query
  dataset validated successfully.
- Offline suite: **45 passed**, two opt-in tests deselected.
- Suite including the cached real CPU model: **46 passed**, GPU test deselected;
  **89% statement coverage**. One upstream deprecated-import warning remains.
- Ruff lint/format, mypy (17 source files), and Git whitespace checks pass.
- Tests cover provenance constraints, references, duplicate/leakage handling,
  code-switch metadata, analytic metric examples, prompt preservation, corrupt
  caches, result serialization, native MTEB score agreement, filtering with the
  full corpus, resume identity, comparison guards, CLI and explicit CUDA errors.
- The CLI independently validated the measured results and generated their report.
- All seven overall metrics in the real-model result agree with native MTEB
  scores within its five-decimal rounding tolerance.
- CI is configured; hosted CI has not been run from this local task.

The first real run is `20260921T051049Z-f9694d9c`, using
`intfloat/multilingual-e5-small` at revision
`614241f622f53c4eeff9890bdc4f31cfecc418b3`, CPU, FP32, batch size 8, seed 42,
maximum sequence length 128. Its downloaded weight file was checked against the
Hub's published SHA-256 before execution. No embedding cache was used.

Measured fixture-only overall scores: Recall@1 **0.7692**, Recall@5/10/20 **1.0000**,
MRR@10 and MAP@10 **0.8590**, nDCG@10 **0.8947**. Three queries have a wrong first
result. These 13 unreviewed queries do not support language comparisons or
significance claims. See the [full report](../reports/cpu-smoke/report.md),
[structured results](../reports/cpu-smoke/result.json) and
[manifest](../reports/cpu-smoke/manifest.json).

The run records its dirty development checkout and source checksum honestly.
Later API cleanup and documentation commits do not rewrite that historical identity.
Reproduction creates a new run identity; timing and floating-point results may vary.

## Reproduction commands

Use Python 3.11–3.13; the verified local version is 3.12.14.

```sh
uv sync --frozen --extra dev
uv run --frozen pytest
uv run --frozen zimmteb datasets validate --output reports/validation
uv run --frozen zimmteb benchmark run --config configs/benchmarks/tiny.yaml --model multilingual-e5-small --device cpu --output runs/first-benchmark
uv run --frozen zimmteb results validate --run runs/first-benchmark
uv run --frozen zimmteb report generate --run runs/first-benchmark --output reports/first-benchmark.md
uv run --frozen zimmteb failures inspect --run runs/first-benchmark
```

The historical local run used `.venv/Scripts/python.exe -m zimmteb` for the same CLI
arguments. Choose a fresh output directory for another run. The model downloads
on first use without credentials; the completed local run used the prefilled
project cache with `HF_HOME=.cache/huggingface` and both `HF_HUB_OFFLINE=1` and
`HF_DATASETS_OFFLINE=1`. Those settings work only once the checkpoint is cached.

To include real CPU inference in tests, run
`uv run --frozen pytest -m "not gpu" --cov=zimmteb`.
Linux's frozen environment uses CPU PyTorch. CUDA needs a separately installed
compatible PyTorch build; `--device cuda` rejects unavailable CUDA explicitly.

## Limitations, debt and Phase 2

All language text and code switching need speaker review. Some domains have no
queries, relevance judgments are sparse, and equivalent texts in other languages
may be false negatives. There are no reviewed cross-language tasks, trained
Zimbabwe-adapted models, reranking implementation or scientific baseline comparison.
SONAR remains optional and deferred. E5 is the only real checkpoint executed here.

Exact search retains corpus embeddings in RAM; validation's near-duplicate check
is quadratic. Replace these only when real corpus scale warrants it. Resume accepts
complete matching runs; interrupted runs reuse embeddings through a new output
directory rather than resuming arbitrary intermediate evaluation state.

Timing is a single smoke measurement without controlled warmup or repeated trials.
Phase timing and reported runtime begin after upstream library imports; they do
not include cold Python process startup.
Sampled process RAM includes library overhead; batched milliseconds are not request
latency. Snapshot disk bytes include auxiliary files. GPU execution, other OS/Python
combinations and hosted CI are not verified locally. Initial Windows native-library
imports took several minutes; subsequent runs completed, and a root cause was not
established. The tested scientific stack is pinned for reproducibility.

Phase 2 should prioritize consented, licensed, speaker-reviewed data; adjudicated
multi-positive judgments; source-separated train/dev/test splits; natural switching;
and directional retrieval. Then run repeated controlled E5/MiniLM/BGE/AfriE5
baselines, validate CUDA resource measurements, and add scale-appropriate search and
source-cluster uncertainty estimates. Training and reranking should follow those
data and evaluation checks, with publication governed by the documented review process.
