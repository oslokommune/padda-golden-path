# Padda Golden Path

Golden paths for **Padda** — the data platform for data engineers at Oslo kommune. This repo contains:

- Zensical documentation (`docs/`) published to GitHub Pages
- Reference implementations of Databricks pipelines (`examples/`)
- Shared Python libraries (`libs/padda.common`, `libs/padda.pipelines`)
- Padda Asset Bundle Templates (`bundle-templates/`)

Official documentation: https://oslokommune.github.io/padda-golden-path/

## Getting started

Install dependencies:

```bash
uv sync
```

To also install documentation tooling:

```bash
uv sync --extra docs
```

## Commands

```bash
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

# Serve docs locally (Zensical, port 8000)
uv run --extra docs zensical serve

# Build docs (writes to site/)
uv run --extra docs zensical build

# Validate Declarative Automation Bundles
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

Zensical documentation with Oslo kommune Punkt design system theming. Configuration in `zensical.toml`. Navigation is defined in `zensical.toml` under `nav`. Supports Mermaid diagrams.

Key CSS files:
- `docs/zensical-stylesheets/punkt-tokens.css` — Punkt design tokens (colors, spacing, fonts from CDN)
- `docs/zensical-stylesheets/oslo-theme.css` — Oslo kommune theme overrides for Zensical
- `docs/overrides/main.html` — template override for font preloading

The theme follows Oslo kommune's visual profile: white header, no rounded corners, no drop shadows, Oslo Sans font, and Punkt color tokens.

Docs are deployed to GitHub Pages via the `pages` workflow on push to main.

## Code style

- Python 3.13+, modern type hints (`dict[str, Any]`, `str | None`)
- Ruff with preview mode, double quotes, LF line endings
- Google-style docstrings
- Lint rules: E, F, W, I (isort), B (bugbear), UP (pyupgrade)
- First-party imports: `common`, `pipelines`, `etl_job`, `golden_path`

## GitHub Actions

Four workflows run on this repo:

- **pr.yaml** — on every PR: format check → lint → DAB validate → DAB plan. Uses GitHub OIDC for Databricks auth (no hardcoded secrets).
- **pages.yml** — on push to `main`: deploys Zensical docs to GitHub Pages.
- **docs-review.yml** — on PRs that touch `docs/`: Claude (via AWS Bedrock) reviews changes against Diataxis, flags duplicates, checks `zensical.toml` navigation, and comments on style deviations. Posts inline comments plus a sticky summary comment.
- **databricks-feed-watcher.yml** — weekdays at 07:00 UTC (manual trigger also available): fetches the Databricks release-notes RSS feed, asks Claude to judge whether each new entry is relevant to this repo, `padda-iac`, or `padda-databrikker`, and posts relevant items to Slack.

The Claude-powered workflows run on AWS Bedrock via OIDC (no Anthropic API key). The feed watcher additionally uses a GitHub App for read-only cross-repo access.

## pytest configuration

`pythonpath` in `pyproject.toml` includes `src`, `examples/api_ingest/src`, and `examples/etl/src` so imports work without installation.
