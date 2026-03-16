.PHONY: docs-serve docs-build

docs-serve:
	uv run --extra docs zensical serve

docs-build:
	uv run --extra docs zensical build
