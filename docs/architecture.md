# Architecture

ZimMTEB owns task data, governance and experiment context. MTEB executes retrieval
evaluation; Sentence Transformers loads and encodes models behind a neutral adapter.
All models, including future locally adapted ones, follow the same route.

```mermaid
flowchart TD
  A[Licensed or original sources] --> B[Provenance and versioned manifests]
  B --> C[Typed validation and leakage audit]
  C --> D[ZimMTEB dataset registry]
  D --> E[MTEB retrieval task]
  E --> F[MTEB search protocol bridge]
  F --> G[Neutral embedding adapter]
  G --> H[Sentence Transformers]
  G --> I[Future optional adapters]
  H --> J[Content-addressed embeddings]
  I --> J
  J --> K[Exact dense search]
  K --> L[MTEB metric evaluation]
  L --> M[Native MTEB result and ZimMTEB envelope]
  M --> N[Language and domain slices]
  N --> O[Markdown report and failure audit]
```

`config.py` loads validated declarative registries from checkout or packaged resources.
`datasets/` owns schemas, loading and validation. `models/` is the model boundary.
`tasks.py` is the isolated MTEB compatibility surface. `runner.py` orchestrates the
run, seeds, manifests and cleanup. `metrics.py` derives per-query audit metrics with
the same trec_eval engine; an integration test checks agreement with MTEB aggregate
nDCG. `results.py` defines the exchange schema; `reporting.py` preserves all slices.

The small module layout deliberately avoids empty manager/factory hierarchies. Training,
mining and non-retrieval task modules will be introduced with real implementations.

Future training (not implemented):

```mermaid
flowchart LR
  A[Training data] --> B[Quality and split checks]
  B --> C[Hard-negative mining and review]
  C --> D[Sentence Transformers trainer]
  D --> E[zim-embed-small checkpoint]
  E --> F[Unchanged ZimMTEB evaluation]
  F --> G[Failure analysis and model card]
```

Future reranking (not implemented):

```mermaid
flowchart LR
  Q[Query] --> E[Embedder]
  E --> K[Top-K candidates]
  K --> C[CrossEncoder]
  C --> R[Reranked candidates]
  R --> M[Quality and added latency]
```
