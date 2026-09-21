# ZimMTEB

**Zimbabwe Multilingual Text Embedding Benchmark**

A benchmark and model-engineering platform for retrieval, reranking, semantic
representation, and efficient multilingual embeddings across Zimbabwean English,
chiShona, isiNdebele, and code-switched text.

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License Apache 2.0](https://img.shields.io/badge/code-Apache--2.0-green)
![Phase 1](https://img.shields.io/badge/status-synthetic%20infrastructure-orange)

**Phase 1 implements retrieval infrastructure.** Training, reranking, additional task
families and a public leaderboard are planned. Neither `zim-embed-small` nor
`zim-reranker` exists as a trained release.

**The first real-model CPU smoke run is complete.** Its scores are measured on
synthetic fixtures and validate infrastructure, not representative language quality.
See the [Phase 1 engineering report](docs/phase1-engineering-report.md) for verification
details and commands. A reviewed linguistic benchmark remains future work.

**Phase 2 is in progress across all eight domains.** Directional retrieval,
source-family leakage checks and review packets are implemented. Public-source
candidates are documented; reviewed multilingual data is not yet released.
See the [Phase 2 plan and workflow](docs/phase2-plan.md).
An [unreviewed public-source seed pilot](docs/review/pilot-status.md) is prepared locally.
The [volunteer recruitment issue](https://github.com/tdrzzie/zimmteb/issues/1) is open.

## Why ZimMTEB

Global averages can conceal weak performance in underrepresented languages, local
domains and code-switching. ZimMTEB asks how retrieval quality varies across Zimbabwean
settings, and whether smaller adapted models can approach larger systems at lower
cost. It extends MTEB and Sentence Transformers rather than forking them. Future
local models use the same evaluation infrastructure as third-party baselines.

## Research questions

- How do English, chiShona, Northern Ndebele and their code-switch tracks differ?
- What changes under cross-language retrieval and Zimbabwe-relevant domains?
- Do Africa-specialized models improve on general multilingual baselines?
- How do hard negatives, distillation and reranking affect quality and cost?
- Can compact adapted models approach larger models on consumer hardware?

Answering these requires reviewed data and controlled experiments beyond Phase 1.

## Languages and domains

| Track | Code | Current data |
|---|---|---|
| Zimbabwean English | `eng` | Synthetic, unreviewed |
| chiShona | `sna` | Synthetic, unreviewed |
| Northern isiNdebele | `nde` | Synthetic, unreviewed |
| English–Shona | `eng-sna-codeswitch` | Artificial switching, unreviewed |
| English–Ndebele | `eng-nde-codeswitch` | Artificial switching, unreviewed |

Northern Ndebele is not Southern Ndebele (`nbl`) or Zulu (`zul`). Registries define
financial services, mobile payments, telecommunications, agriculture, education,
public information, customer support and technology support. Some domains have
corpus documents but no evaluated queries; reports expose missing coverage.

## Architecture

```mermaid
flowchart LR
  A[Provenance and data] --> B[Validation]
  B --> C[MTEB retrieval task]
  C --> D[Neutral model adapter]
  D --> E[Embeddings and search]
  E --> F[MTEB metrics]
  F --> G[Versioned results]
  G --> H[Sliced reports and failures]
```

MTEB owns task conventions, evaluation and native results. Sentence Transformers
owns model loading and encoding. ZimMTEB adds registries, provenance, validation,
caching, run identity, resource measurement and sliced reporting.
See [architecture](docs/architecture.md) and [upstream research](docs/research/upstream-landscape.md).

## Installation and quick start

Use Python 3.11–3.13; Python 3.12 is the local target. Install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
uv sync --frozen --extra dev
uv run zimmteb system info
uv run zimmteb datasets validate
uv run pytest
```

Alternatively, `python -m pip install -e '.[dev]'` installs without uv but does not
consume the uv lockfile. No token is needed. Core dependencies include MTEB and
Sentence Transformers; SONAR/Fairseq2 are not required. Training/reporting extras
prepare later workflows, not finished features.

The lockfile pins MTEB 2.21.0, Sentence Transformers 6.1.0 and PyTorch 2.8.0.
Linux uv installs use the official CPU PyTorch index. CUDA users need a separate
environment with a compatible CUDA PyTorch wheel; a frozen CPU environment does
not become CUDA-capable merely by selecting `--device cuda`.

## Run a benchmark

First real-model CPU run (downloads one small multilingual checkpoint):

```sh
uv run zimmteb benchmark run --config configs/benchmarks/tiny.yaml --model multilingual-e5-small --device cpu --output runs/first-benchmark
uv run zimmteb results validate --run runs/first-benchmark
uv run zimmteb report generate --run runs/first-benchmark --output reports/first-benchmark.md
uv run zimmteb failures inspect --run runs/first-benchmark
```

Offline pipeline test:

```sh
uv run zimmteb benchmark run --model test-hash --output runs/mock-smoke
```

`test-hash` is a lexical test fixture, not a multilingual model baseline. Real runs
use immutable revisions. Outputs contain manifests, native MTEB JSON, enriched
results, predictions and Markdown. Use fresh output paths; `--resume` requires a
complete run with identical inputs. `--cache .cache/embeddings` enables safe reuse;
cache hits are labeled and should not be used for cold-inference comparisons.

Language/domain filters select queries while retaining the full corpus:

```sh
uv run zimmteb benchmark run --model multilingual-e5-small --language sna --task retrieval --domain agriculture --output runs/shona-agriculture
```

CLI groups: `system`, `languages`, `domains`, `datasets`, `models`, `benchmark`,
`results`, `report`, `failures`. Each supports `--help`.

## Tasks and baselines

Implemented: dense retrieval, Recall@1/5/10/20, MRR@10, nDCG@10 and MAP@10.
Directional retrieval is implemented; it requires explicit cross-language judgments.
Planned: reranking, STS, classification and bitext tasks with dedicated data.
The current mixed corpus is not a validated cross-lingual benchmark.

| Configuration | Role | Status |
|---|---|---|
| `multilingual-e5-small` | Small multilingual retriever | Primary Phase 1 model |
| `multilingual-minilm` | Compact alternative | Pinned configuration |
| `bge-m3` | Larger dense baseline | Configuration; no result claimed |
| `afrie5` | Africa-specialized baseline | Configuration; no result claimed |
| `sonar` | Optional research baseline | Adapter deferred; Northern Ndebele absent from inspected text card |

Prompt settings, revisions and licenses are in `configs/models`. No winners are
hard-coded. Native FlagEmbedding, sparse and multi-vector evaluation are deferred.

## Dataset design and code-switch evaluation

The fixture has **13 queries and 16 documents**, all test-only, original AI-drafted,
synthetic and unreviewed. It does not establish translation accuracy, native-speaker
usage or natural switching. Documents are stored once; queries reference IDs.
Versioned manifests protect exact bytes with checksums.

Validation checks required provenance, references, duplicate IDs/text, Unicode,
length warnings, contradictory judgments, cross-split overlap and heuristic near
duplicates. Semantic leakage and language quality still need human review.
Code-switch tracks carry partner, direction, ratio, origin and review metadata and
remain separate in reports. See [data design](docs/dataset-design.md) and
[governance](DATA_GOVERNANCE.md).

## Results and efficiency

Reports expose overall, language, domain, code-switch, language/domain and
language-pair slices, missing coverage and mechanical ranking failures. Model load,
indexing, query encoding and ranking timing are separate. Amortized batch timing is
not production request latency; sampled RAM and allocator VRAM have limitations.
Missing measurements remain null. See [evaluation](docs/evaluation.md).

`benchmark compare --left RUN_A --right RUN_B` rejects incompatible datasets/query
sets and provides an illustrative paired bootstrap. This tiny correlated fixture
cannot support scientific superiority claims.

## Training and hardware

Training `zim-embed-small` and `zim-reranker` is deferred until reviewed training
data exists. [Training design](docs/model-training.md) covers current trainers,
hard-negative mining, cached losses, false-negative controls and distillation.
Card templates are in `hf_templates`; nothing is published automatically.

CPU is the default. `--device auto` selects available hardware; explicit CUDA
requires a CUDA-capable PyTorch build. The RTX 4060 profile targets 8 GB VRAM.
OOM errors advise smaller batches/length without silently changing devices.
No enterprise GPU or cloud service is required.

## Reproducibility and structure

Runs record configs, model revision, dataset hashes, source identity, versions,
seed and hardware. [Reproducibility guide](docs/reproducibility.md).

```text
src/zimmteb/        CLI, data, adapters, MTEB integration, results, reports
configs/           Language/domain/model/benchmark/hardware definitions
datasets/          Versioned manifest and synthetic JSONL fixture
tests/             Unit and offline integration; opt-in network/GPU tests
docs/              Research, design, reproducibility and 12 ADRs
hf_templates/      Dataset and future model cards
scripts/           Fixture generator and tracked-artifact guard
.github/workflows/ Credential-free quality checks
```

## Roadmap

| Version | Focus |
|---|---|
| v0.1 | Retrieval infrastructure and synthetic smoke data |
| v0.2 | Initial reviewed language tracks and directional retrieval |
| v0.3 | Controlled E5, BGE, AfriE5 and compact baselines |
| v0.4 | Speaker review, natural switching and stronger judgments |
| v0.5 | Hard-negative mining and `zim-embed-small` |
| v0.6 | CrossEncoder baselines, `zim-reranker`, latency/quality |
| v0.7 | Approved Hugging Face data/model/leaderboard publication |
| v1.0 | Stable reviewed benchmark, technical report, possible upstream tasks |

## Contributing, attribution, citation and license

See [contributing](CONTRIBUTING.md), [security](SECURITY.md),
[attribution](ATTRIBUTION.md) and [licensing](docs/decisions/0002-licensing.md).
No hosted leaderboard or upstream endorsement is implied. Until a paper/DOI exists,
cite software version and exact commit alongside MTEB, MMTEB and Sentence Transformers.

Code: [Apache-2.0](LICENSE). Original synthetic data: [CC0-1.0](datasets/LICENSE.md).
Third-party weights retain their own licenses.
