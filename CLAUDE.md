# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Golden paths for **Padda** — the data platform for data engineers at Oslo kommune. The repo contains:

- MkDocs documentation (`docs/`) published to GitHub Pages
- Reference implementations of Databricks pipelines (`examples/`)
- Shared Python libraries (`libs/padda.common`, `libs/padda.pipelines`)
- Databricks Asset Bundle (DAB) templates (`src/golden_path/dab-simple/`)

Official documentation: https://oslokommune.github.io/padda-golden-path/

## Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Tests with coverage
uv run pytest --cov=libs

# Run a single test
uv run pytest examples/api_ingest/tests/test_client.py -k "test_name"

# Lint and format
uvx ruff check . --fix
uvx ruff format .

# Format check (as CI runs it)
uv format --check

# Install pre-commit hooks
uvx pre-commit install

# Serve docs locally
uv run --extra docs mkdocs serve

# Build docs
uv run --extra docs mkdocs build

# Validate Databricks bundles
databricks bundle validate
```

## Architecture

### uv workspace

The project uses uv as package manager with a workspace setup. The root `pyproject.toml` defines workspace members:
- `libs/padda.pipelines` — pipeline utilities
- `libs/padda.common` — shared utilities (logging, config)

### Databricks Asset Bundles (DAB)

`databricks.yml` at the root aggregates example bundles via `include`. Each example (`examples/api_ingest/`, `examples/excel_ingest/`) has its own `bundle.yml` with job definitions, cluster configuration, and variables.

The pattern follows the **medallion architecture**: Bronze (raw data from landing zone) → Silver (cleaned) → Gold (business-ready).

### Examples

Each example under `examples/` is a self-contained pipeline with:
- `src/` — Python source code
- `tests/` — pytest tests
- `notebooks/` — Databricks notebooks
- `resources/` — YAML job definitions
- `bundle.yml` — DAB configuration

### Documentation

MkDocs with Material theme. Navigation structure in `mkdocs.yml`. Supports Mermaid diagrams, Excalidraw, and Notion sync. Custom gen-files scripts in `docs/mkdocs_extension/` generate navigation automatically.

## Code style

- Python 3.13+, modern type hints (`dict[str, Any]`, `str | None`)
- Ruff with preview mode, double quotes, LF line endings
- Google-style docstrings (parsed by mkdocstrings)
- Lint rules: E, F, W, I (isort), B (bugbear), UP (pyupgrade)
- First-party imports: `common`, `pipelines`, `etl_job`, `golden_path`

## CI

PR workflow (`pr.yaml`) runs: format check → lint → DAB validate → DAB plan. Uses GitHub OIDC for Databricks auth (no hardcoded secrets). Docs are deployed to GitHub Pages on push to main.

## pytest configuration

`pythonpath` in `pyproject.toml` includes `src`, `examples/api_ingest/src`, and `examples/etl/src` so imports work without installation.

## Agent rules

- **Never fabricate information.** Only state things you have evidence for from the codebase, documentation, or tool results. Do not invent URLs, API endpoints, file paths, or configuration values.
- **All file content must be in English.** This includes code, comments, docstrings, commit messages, and documentation files. The only exception is the interactive conversation with the user, which should be in Norwegian.
- **Never suggest committing or pushing.** Do not prompt the user to commit or push changes. The user will explicitly ask when they want to commit or push.
- **Never include code from this repository in web searches.** When performing web searches, use only keywords and general terms to formulate good queries. Never send source code, configuration snippets, or other file contents from this repo as part of a search query.
