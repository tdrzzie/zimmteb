.PHONY: install check test smoke report
install:
	uv sync --frozen --extra dev
check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy
test:
	uv run pytest
smoke:
	uv run zimmteb benchmark run --model test-hash --output runs/ci-smoke
report:
	uv run zimmteb report generate --run runs/first-benchmark --output reports/first-benchmark.md
