# Padda Golden Path

```text
 _________________________________
|                                 |
| Don't panic! Share your data!   |
|___  ____________________________|
    \/
  @..@
 (----)
(>____<)
^^ ~~ ^^
```

Golden paths for **Padda** — the data platform for data engineers at Oslo kommune. This repo contains:

- Zensical documentation (`docs/`) published to GitHub Pages
- Padda Asset Bundle Templates (`bundle-templates/`)
- A bundle for the Databricks Security Analysis Tool (`bundles/sat-tool/`), synced from upstream

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
# Lint and format
uvx ruff check . --fix
uvx ruff format .

# Format check (as CI runs it)
uvx ruff format --check

# Install pre-commit hooks
uvx pre-commit install

# Serve docs locally (Zensical, port 8000)
uv run --extra docs zensical serve

# Build docs (writes to site/)
uv run --extra docs zensical build
```

## Architecture

Example bundles live in [`padda-databrikker`](https://github.com/oslokommune/padda-databrikker),
the reference implementation of the golden path.

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

## GitHub Actions

Nine workflows run on this repo:

- **pr.yaml** — on every PR: ruff format check and lint.
- **pages.yml** — on push to `main`: deploys Zensical docs to GitHub Pages.
- **docs-review.yml** — on PRs that touch `docs/`: Claude (via AWS Bedrock) reviews changes against Diataxis, flags duplicates, checks `zensical.toml` navigation, and comments on style deviations. Posts inline comments plus a sticky summary comment.
- **databricks-feed-watcher.yml** — weekdays at 06:00 UTC (manual trigger also available): fetches the Databricks release-notes RSS feed, asks Claude to judge whether each new entry is relevant to this repo, `padda-iac`, or `padda-databrikker`, and posts relevant items to Slack.
- **collect-metrics.yml** — Mondays at 06:00 UTC: counts jobs, pipelines, and tables per medallion layer across the workspaces in each Databricks account and uploads JSONL to a Unity Catalog volume for the `platform_metrics` pipeline in `padda-databrikker`.
- **collect-aws-cost.yml** — Mondays at 06:00 UTC: queries AWS Cost Explorer per cost-allocation tag and uploads JSONL to the same volume.
- **collect-dora.yml** — daily at 06:30 UTC: records this repo's merged PRs as DORA deployment and lead-time events, uploaded to the same volume. Copied verbatim to every platform repo.
- **weekly-report.yml** — Mondays at 08:00 UTC: posts a Slack summary of PRs merged in `padda-golden-path`, `padda-iac`, and `padda-databrikker`.
- **sat-upstream.yml** — Mondays at 07:00 UTC: syncs `bundles/sat-tool/` with the upstream Databricks Security Analysis Tool and opens a PR when it has moved.

The Claude-powered workflows run on AWS Bedrock via OIDC (no Anthropic API key). The feed watcher additionally uses a GitHub App for read-only cross-repo access.

## pytest configuration

Root pytest ignores `bundle-templates/` (templated, non-runnable test files) via `addopts`
in `pyproject.toml`.
