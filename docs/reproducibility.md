# Reproducibility

Use `uv sync --frozen --extra dev` and record `zimmteb system info`. The lockfile pins
the resolved environment; the integration pins MTEB/ST major interfaces explicitly.
CPU inference is the portable default. A CUDA-capable PyTorch build is a separate
environment choice and must be recorded; merely requesting CUDA cannot enable it.

Run identity includes benchmark config, model config and immutable revision, exact
dataset bytes/manifest, seed, effective device, package versions, Git commit/dirty
state and source checksum. Local models receive an additional content checksum.
Seeds reduce stochastic variation but do not promise cross-platform bitwise equality.

Each run writes `manifest.json`, `mteb-results.json`, `result.json`, predictions and
`report.md`. Keep these together. `--resume` returns a complete matching result;
it refuses changed inputs. For interruption recovery use a fresh output directory
with the same embedding cache. Cache keys include role and exact ordered text.
Never compare cached phase timing with uncached inference timing.

No checkpoint is committed. Public models download to the Hugging Face cache on the
first real run. Set `HF_HOME` to choose a cache location. Tests use no credentials.
For offline runs, prefetch the pinned checkpoint, then set `HF_HUB_OFFLINE=1` and
`HF_DATASETS_OFFLINE=1`. The repository's synthetic dataset is bundled in the wheel.
