# Contributing

Install Python 3.11+ (3.12 is the tested local target) and uv, then:

```sh
uv sync --frozen --extra dev
uv run pre-commit install
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
```

Normal tests use a deterministic mock adapter and real MTEB evaluation; they do
not download checkpoints. Real inference tests require explicit `pytest -m network`;
CUDA tests require `pytest -m gpu`. Run expensive baseline sweeps manually, with
reviewed configurations and a fresh output directory per run. No paid APIs or cloud
resources are created by CI.

Changes should include a clear problem statement, tests for meaningful behavior,
and updated documentation. Add data only with provenance and license evidence.
Keep Northern Ndebele (`nde`) distinct from Southern Ndebele (`nbl`). New language
tracks belong in registries; do not scatter language-specific branches through code.
Do not regenerate released fixtures without versioning. Preserve benchmark neutrality.

The repository uses Apache-2.0 for code and CC0-1.0 for the original synthetic fixture.
Contributors must have rights to contributed material. No upstream endorsement is implied.
