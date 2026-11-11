# Databricks Asset Bundle conventions (Padda)

Source of truth: `docs/referanse/databricks-bundles.md` and `bundle-templates/` in
`padda-golden-path`.

## Standard folder structure

```
<bundle-name>/
├── databricks.yml        # main bundle config: name, artifacts, variables, targets
├── resources/            # one YAML per job/pipeline, included via glob
│   └── *.yml
├── src/<package_name>/   # Python code, built as a wheel
├── notebooks/            # notebook tasks and exploration
├── tests/                # pytest (conftest.py provides a local Spark session)
└── pyproject.toml        # uv + hatchling; package_name = bundle name with - → _
```

`bundle.name` is used as prefix and root path — keep it kebab-case and descriptive of
the domain (`excel-ingest`, `folkeregister-innlasting`). `include:` uses globs
(`resources/*.yml`) so new job files are picked up without editing `databricks.yml`.

## Naming

| Thing | Convention | Example |
|-------|-----------|---------|
| Bundle name | kebab-case | `excel-ingest` |
| Job YAML key | snake_case + `_job` | `ingest_excel_job` |
| Task key | snake_case + `_task` | `python_task` |
| Cluster key | snake_case | `job_cluster` |
| Variables | snake_case | `catalog`, `excel_input_path` |

## Targets: stage and prod

The current template defines two targets. Older bundles use `dev`/`prod` — functionally
the same, but new bundles use `stage`/`prod` and existing ones should migrate when
convenient.

```yaml
targets:
  stage:
    mode: development     # prefixes resources "[dev <user>]", pauses schedules
    default: true
    presets:
      artifacts_dynamic_version: true   # avoids stale wheels cached on clusters
    variables:
      catalog: <stage_catalog>
      schema: default

  prod:
    mode: production
    workspace:
      host: https://<prod-host>.cloud.databricks.com
      root_path: ~/.bundle/${bundle.name}/${bundle.target}
    run_as:
      service_principal_name: <org>-gha-deploy
    variables:
      catalog: <prod_catalog>
      schema: production
```

Why this shape:

- `mode: development` gives per-user isolation and paused schedules, so several
  developers can deploy the same bundle without colliding.
- `mode: production` **fails deploy unless `run_as` or `permissions` is set** — this is
  deliberate: prod jobs must run as a service principal (`<org>-gha-deploy`), not a
  personal user that may lose access.
- Explicit prod `root_path` keeps deployments stable and predictable across CLI
  versions.

Useful built-in variables: `${workspace.current_user.userName}`, `${bundle.name}`,
`${bundle.target}`.

## Artifacts (Python wheels)

```yaml
artifacts:
  platform:
    type: whl
    path: .
    build: uv build --wheel
```

Reference the wheel in jobs via `${workspace.root_path}/artifacts/.internal/*.whl`.
Only `whl` artifacts are supported. Keep `artifacts_dynamic_version: true` in stage so
clusters do not serve cached old wheels.

## Compute

**Serverless is the default.** Declare an `environments` block and reference it with
`environment_key` per task:

```yaml
resources:
  jobs:
    my_domain_job:
      environments:
        - environment_key: default
          spec:
            client: "3"
            dependencies:
              - ${var.wheel_path}
      tasks:
        - task_key: main_task
          environment_key: default
          python_wheel_task:
            package_name: my_domain
            entry_point: main
```

Use a classic `job_cluster` only when there is a concrete need (e.g. specific instance
types, VPC constraints). If you do: current platform baseline is
`spark_version: 17.3.x-scala2.13`, single-user security mode, modest autoscale (1–2
workers) unless the workload proves otherwise.

Task types available: `notebook_task`, `python_wheel_task`, `spark_python_task`.

## Cost tags (required)

Every job (and classic cluster via `custom_tags`) carries:

```yaml
tags:
  CostTeam: <team>        # e.g. padda
  CostProcess: <process>  # e.g. Ingest, Transform
```

These feed the platform cost breakdown — untagged jobs make spend unattributable.

## UC Volumes

Team-owned volumes can be declared in the bundle:

```yaml
resources:
  volumes:
    my_volume:
      catalog_name: ${var.catalog}
      schema_name: default
      name: my_volume
      volume_type: MANAGED
```

## Responsibility split: bundle vs padda-iac

| Lives in team bundle repo | Lives in `padda-iac` (Terraform) |
|---------------------------|----------------------------------|
| Jobs, tasks, triggers | Workspaces |
| Declarative pipelines | Unity Catalog catalogs |
| Team volumes | Shared schemas (`bronze_default`, …) |
| Team-specific resources | Network, landing zone, IAM, senders |

If a user asks to create a catalog, schema, sender, or workspace-level resource from a
bundle: stop and redirect to `padda-iac` / the platform team.

## Deploy workflow

```bash
databricks bundle validate           # always before deploy
databricks bundle deploy             # deploys default target (stage)
databricks bundle deploy --target prod
```

CI (GitHub Actions with OIDC) runs format → lint → `bundle validate` → `bundle plan`
on PRs. Prod deploys happen via CI as the service principal, not from laptops.
