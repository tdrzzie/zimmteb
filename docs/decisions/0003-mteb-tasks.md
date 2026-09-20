# 0003 — Local tasks with an upstream contribution path

Status: accepted.

Implement `AbsTaskRetrieval` with `TaskMetadata`, HF Dataset-backed corpus/queries and
relevance judgments. `MTEBSearchBridge` implements the current search protocol.
Call `mteb.evaluate` and save its native `ModelResult`; do not replace MTEB with a
standalone metric loop. A local Benchmark groups the task without mutating upstream
registries. Use a local placeholder dataset path and checksum revision, overridden
by local loading. Mark the task private to avoid accidental public treatment.

Upstream submission needs a real stable dataset repository, reviewed examples,
appropriate language/task metadata and contribution review. The synthetic fixture
is unsuitable. No `mteb.get_benchmark("ZimMTEB")` integration is claimed.
