---
name: ok-data-skill
description: Padda golden-path assistant for Databricks data engineering in Oslo kommune. Use whenever the user wants to create a new Databricks Asset Bundle, data pipeline, ingestion job, or data product on the Padda platform, or asks how to structure bronze/silver/gold tables, Auto Loader ingestion, data quality checks (expectations/DQX), bundle naming, deploy targets, cost tags, or dataproduct.yaml metadata — even if they never mention "golden path" or this skill by name. Scaffolds new bundles from the official golden-path template and applies platform conventions when reviewing or writing pipeline code.
---

# ok-data-skill — Padda golden path for Databricks

This skill encodes the conventions of the **Padda** data platform (Oslo kommune, team
Dataspeilet): Databricks + Unity Catalog + AWS S3. It has two jobs:

1. **Create** — scaffold new Databricks Asset Bundles via the `ok data init` flow.
2. **Use** — help developers write pipelines, Spark code, and data-product metadata
   that follow the golden path.

The authoritative sources are the docs and templates in the `padda-golden-path` repo.
When this skill and those docs disagree, the docs win — read them and mention the
discrepancy to the user so the skill can be updated.

Conversation with the user is in Norwegian; all generated file content (code, comments,
YAML, docs) is in English. Never commit or push unless explicitly asked.

## Quick conventions (always apply)

- **Naming**: bundle names kebab-case (`excel-ingest`); job YAML keys snake_case with
  `_job` suffix; task keys snake_case with `_task` suffix; variables snake_case.
- **Targets**: `stage` (mode `development`, default) and `prod` (mode `production`).
  Older bundles use `dev`/`prod`; when touching them, suggest migrating to `stage`/`prod`.
  Production requires `run_as` (service principal) or `permissions`, plus an explicit
  `root_path: ~/.bundle/${bundle.name}/${bundle.target}`.
- **Layers**: landing zone (S3) → `bronze_default` → `silver_default` → `gold_default`
  schemas. Gold tables are the data products.
- **Cost tags**: every job/cluster gets `CostTeam` and `CostProcess` custom tags.
- **Tooling**: Python 3.13+, uv, hatchling wheels, ruff, pytest. Serverless compute is
  the default; classic clusters only when there is a concrete reason.
- **Responsibility split**: workspaces, catalogs, shared schemas, and network live in
  `padda-iac` (Terraform) — never in a bundle. Bundles own jobs, pipelines, team
  volumes, and team-specific resources.

## Mode 1: `ok data init` — scaffold a new bundle

Trigger: the user types `ok data init` (or asks to create/start a new bundle, domain,
pipeline project, or data product skeleton).

The scaffold comes from the official Databricks Asset Bundle template in
`bundle-templates/` in the `padda-golden-path` repo. Always use that template rather
than writing files by hand — it is the single source of truth and evolves over time.

### Step 1: Gather inputs

Ask the user for anything you cannot infer (use their answers as-is; the template
validates patterns):

| Field | Constraint | Notes |
|-------|-----------|-------|
| `domain_name` | `^[A-Za-z0-9_-]+$` | Bundle/directory name, kebab-case preferred. Package name is derived automatically (`-` → `_`). |
| `domain_description` | free text | One sentence about the domain. |
| `catalog_name` | `^[a-z0-9_]+$` | Target Unity Catalog. Found in 1Password / from the platform team. |
| `stage_workspace_host` | `https://…` | Stage Databricks workspace URL. |
| `prod_workspace_host` | `https://…` | Prod Databricks workspace URL. |
| `setup_type` | `default` \| `minimal` \| `tailored` | `default` is right for most teams (includes example jobs). |

If the workspace hosts are unknown, point the user to 1Password or the platform team —
do not guess URLs.

### Step 2: Run the template non-interactively

Write the answers to a JSON config file (in a temp/scratch location, not the repo):

```json
{
  "catalog_name": "...",
  "stage_workspace_host": "https://...",
  "prod_workspace_host": "https://...",
  "domain_name": "...",
  "domain_description": "...",
  "setup_type": "default",
  "include_example_jobs": "yes",
  "empower_vscode": "yes"
}
```

Then run, from the directory where the new bundle should be created:

```bash
databricks bundle init <path-to-padda-golden-path>/bundle-templates \
  --config-file <config.json> --output-dir .
```

Locate the local `padda-golden-path` checkout first (it is usually a sibling of the
current repo). If no local checkout exists, use the GitHub form documented in
`bundle-templates/README.md`. Requires Databricks CLI ≥ v0.236.0.

### Step 3: Validate and orient

1. `cd <domain_name> && databricks bundle validate` — fix any issues before handing over.
2. Check that jobs carry `CostTeam`/`CostProcess` tags; add them if the template output
   lacks them (see `references/bundle-conventions.md`).
3. Walk the user briefly through what was generated: `databricks.yml` (stage/prod
   targets), `resources/` (job definitions), `src/<package>/` (wheel code),
   `notebooks/`, `tests/`.

### Step 4: Ask the data-product question

Ask the user (in Norwegian): **is this bundle going to produce a data product** — a
gold-layer dataset that others outside the team will consume — or is it an internal
pipeline?

- **Data product** → generate a `dataproduct.yaml` in the bundle root from
  `assets/dataproduct.yaml` and fill in what the user knows (owner, steward, technical
  owner, classification, purpose). Set `lifecycleStatus: draft`. See
  `references/data-product.md` for field semantics before filling it in.
- **Internal pipeline** → skip the file, but mention that if a gold table later gets
  external consumers, it becomes a data product and needs metadata and an owner.

## Mode 2: Working on pipelines and bundles

When the user is writing or reviewing Spark code, pipeline SQL, bundle YAML, or asking
"how should I…" questions, load the relevant reference before answering:

| Topic | Read |
|-------|------|
| Bundle structure, `databricks.yml`, targets, presets, artifacts, serverless vs classic compute, naming, cost tags | `references/bundle-conventions.md` |
| Medallion layers, Auto Loader / ingestion patterns, bronze/silver/gold Spark & SQL conventions, data quality (constraints, expectations, DQX), storage & performance | `references/medallion-spark.md` |
| Data product thinking: roles, lifecycle, `dataproduct.yaml`, access vs usage rights, versioning and breaking changes | `references/data-product.md` |

Ground answers in these conventions rather than generic Databricks advice — the
platform has made deliberate choices (serverless-first, string-typed bronze,
`*_default` schemas, sensitivity prefixes) and code that ignores them creates friction
for the next team. When the user's situation genuinely falls outside the conventions,
say so explicitly instead of forcing a fit, and suggest they raise it with the
platform team.

For deeper answers, the full documentation lives in `padda-golden-path/docs/`
(Norwegian): `referanse/` (reference), `guider/` (how-to), `om-plattformen/konsepter/`
(concepts), `kom-i-gang/` (tutorials).
