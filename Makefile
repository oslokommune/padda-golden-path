.PHONY: docs-serve docs-build docs-v2-serve docs-v2-build

docs-serve:
	uv run --extra docs zensical serve

docs-build:
	uv run --extra docs zensical build

docs-v2-serve:
	uv run --extra docs zensical serve -f zensical-v2.toml -a localhost:8001

docs-v2-build:
	uv run --extra docs zensical build -f zensical-v2.toml
