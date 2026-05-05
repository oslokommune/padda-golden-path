# System Tables Dashboards - Databricks Asset Bundle

This bundle deploys the community Databricks Dashboard Suite into an SRA-style
workspace where clusters and serverless jobs should not depend on outbound
internet access.

Source dashboard definitions are vendored from:

https://github.com/mohanab89/databricks-dashboard-suite

## What This Bundle Does

- Syncs dashboard definitions as `dashboard_templates/*.lvdash.json.tmpl`.
- Runs a one-time serverless initializer notebook.
- Installs `databricks-sdk` from bundled wheels, not PyPI.
- Creates helper SQL functions in `${var.catalog}.${var.schema}`.
- Creates or refreshes `workspace_reference` and `warehouse_reference`.
- Uses bundled workspace ID/name mappings from `data/workspace_reference.csv`
  when available.
- Creates or updates the Lakeview dashboards.
- Publishes the dashboards with a SQL warehouse.
- Optionally grants `CAN_READ` to a workspace group.

The templates intentionally do not use a raw `.lvdash.json` extension. Raw
dashboard files synced by bundles can be interpreted as dashboard resources and
produce duplicate broken dashboards. The initializer reads the `.tmpl` files and
imports them through the Lakeview API instead.

## Prerequisites

- Databricks CLI authenticated against the target workspace.
- `databricks-sdk` installed locally if you want to generate
  `data/workspace_reference.csv` with `scripts/export_workspace_reference.py`.
- System tables enabled for the schemas used by the dashboards:
  `system.billing`, `system.access`, `system.query`, and `system.lakeflow`.
- A SQL warehouse in the workspace. Set `warehouse_id` explicitly for
  deterministic deployment, or leave it empty and the initializer will pick a
  serverless warehouse first, then the first available warehouse.
- Write permission to the configured catalog and schema.

## Deploy

To show workspace display names in the dashboards without calling the account
API from the target workspace, populate the bundled CSV before deployment:

```bash
python scripts/export_workspace_reference.py \
  --account-id <account-id> \
  --profile <account-cli-profile>
```

Alternatively, pass account service principal credentials directly:

```bash
python scripts/export_workspace_reference.py \
  --account-id <account-id> \
  --client-id <account-service-principal-client-id> \
  --client-secret <account-service-principal-client-secret>
```

This writes `data/workspace_reference.csv` with `workspace_id,workspace_name`
columns. You can also maintain that CSV manually. The initializer reads it first
and falls back to numeric workspace IDs only for IDs that are not present in the
CSV.

```bash
./download_wheels.sh
databricks bundle deploy --target dev
databricks bundle run system_table_dashboards_initializer --target dev
```

To deploy a side-by-side variant whose dashboard queries only show data for the
workspace where the bundle is deployed, set `workspace_scope=current`:

```bash
databricks bundle deploy --target dev \
  --var catalog=<catalog> \
  --var schema=<schema> \
  --var workspace_scope=current

databricks bundle run system_table_dashboards_initializer --target dev \
  --var catalog=<catalog> \
  --var schema=<schema> \
  --var workspace_scope=current
```

Current-workspace deployments are published under a separate
`dashboards_current_workspace` folder and dashboard names are suffixed with
`Current Workspace`. Set `dashboard_variant` to use another label.

For the stage workspace/profile used by DIG Databrikker:

```bash
databricks bundle deploy --target dev \
  --var catalog=dig_databrikker_stage_yellow \
  --var schema=analyst_default \
  -p databrikker-stage

databricks bundle summary --target dev \
  --var catalog=dig_databrikker_stage_yellow \
  --var schema=analyst_default \
  -p databrikker-stage

databricks bundle run system_table_dashboards_initializer --target dev \
  --var catalog=dig_databrikker_stage_yellow \
  --var schema=analyst_default \
  -p databrikker-stage
```

Current-workspace variant for DIG Databrikker stage:

```bash
databricks bundle deploy --target dev \
  --var catalog=dig_databrikker_stage_yellow \
  --var schema=analyst_default \
  --var workspace_scope=current \
  -p databrikker-stage

databricks bundle run system_table_dashboards_initializer --target dev \
  --var catalog=dig_databrikker_stage_yellow \
  --var schema=analyst_default \
  --var workspace_scope=current \
  -p databrikker-stage
```

Because the `dev` target uses `mode: development`, the deployed job name is
prefixed with the target and user name, for example:
`[dev fredrik_lovejord] System Tables Dashboards Initializer`.

Override target variables when needed:

```bash
databricks bundle deploy --target dev \
  --var catalog=<catalog> \
  --var schema=<schema> \
  --var warehouse_id=<warehouse-id>
```

To check the CSV against the account API before deploying:

```bash
python scripts/export_workspace_reference.py --check \
  --account-id <account-id> \
  --profile <account-cli-profile>
```

or:

```bash
python scripts/export_workspace_reference.py --check \
  --account-id <account-id> \
  --client-id <account-service-principal-client-id> \
  --client-secret <account-service-principal-client-secret>
```

Account-level OAuth parameters can still be passed to the initializer as a
runtime fallback when `data/workspace_reference.csv` is unavailable. This
requires the target workspace job to reach the Databricks account API:

```bash
databricks bundle deploy --target dev \
  --var account_id=<account-id> \
  --var client_id=<account-service-principal-client-id> \
  --var client_secret=<account-service-principal-client-secret>

databricks bundle run system_table_dashboards_initializer --target dev \
  --var account_id=<account-id> \
  --var client_id=<account-service-principal-client-id> \
  --var client_secret=<account-service-principal-client-secret>
```

If neither the CSV nor account API credentials provide a workspace, the
`workspace_reference` table uses that workspace ID as its name.
