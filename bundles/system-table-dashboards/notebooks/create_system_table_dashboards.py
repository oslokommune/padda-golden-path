# Databricks notebook source
# MAGIC %md
# MAGIC # System Tables Dashboards Initializer
# MAGIC
# MAGIC Deploys and publishes Databricks system table dashboards from bundled
# MAGIC dashboard templates. Designed for SRA workspaces with no runtime internet
# MAGIC access.

# COMMAND ----------

import csv
import glob
import json
import subprocess
import sys
from pathlib import Path


def _workspace_file_path(path: str) -> str:
    return path if path.startswith("/Workspace") else f"/Workspace{path}"


def _bundle_root() -> str:
    notebook_path = (
        dbutils.notebook.entry_point.getDbutils()
        .notebook()
        .getContext()
        .notebookPath()
        .get()
    )
    root = notebook_path.rsplit("/notebooks/", 1)[0]
    return _workspace_file_path(root)


def install_local_databricks_sdk() -> None:
    wheels_path = f"{_bundle_root()}/wheels"
    wheels = sorted(glob.glob(f"{wheels_path}/*.whl"))
    if not wheels:
        raise RuntimeError(
            f"No wheels found in {wheels_path}. Run ./download_wheels.sh before deploying."
        )

    print(f"Installing databricks-sdk from bundled wheelhouse: {wheels_path}")
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--quiet",
        "--no-index",
        "--find-links",
        wheels_path,
        "databricks-sdk==0.38.0",
    ])


install_local_databricks_sdk()

# COMMAND ----------

from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.service.dashboards import Dashboard
from databricks.sdk.service.iam import AccessControlRequest, PermissionLevel
from pyspark.errors import PySparkException
from pyspark.sql.functions import col
from pyspark.sql.types import StringType

w = WorkspaceClient()

# COMMAND ----------

dbutils.widgets.multiselect(
    "actions",
    "All",
    choices=[
        "All",
        "Deploy Dashboards",
        "Publish Dashboards",
        "Create Functions",
        "Create/refresh Tables",
    ],
)
dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "system_table_dashboards")
dbutils.widgets.text("warehouse_id", "")
dbutils.widgets.text("tags_to_consider_for_team_name", "team_name,group")
dbutils.widgets.text("dashboard_viewers_group", "users")
dbutils.widgets.text("workspace_scope", "account")
dbutils.widgets.text("dashboard_variant", "")
dbutils.widgets.text("workspace_reference_csv", "data/workspace_reference.csv")
dbutils.widgets.text("account_host", "https://accounts.cloud.databricks.com/")
dbutils.widgets.text("account_id", "")
dbutils.widgets.text("client_id", "")
dbutils.widgets.text("client_secret", "")

actions = dbutils.widgets.get("actions")
catalog = dbutils.widgets.get("catalog").strip()
schema = dbutils.widgets.get("schema").strip()
warehouse_id = dbutils.widgets.get("warehouse_id").strip()
tags_to_consider_for_team_name = dbutils.widgets.get(
    "tags_to_consider_for_team_name"
).strip()
dashboard_viewers_group = dbutils.widgets.get("dashboard_viewers_group").strip()
workspace_scope = dbutils.widgets.get("workspace_scope").strip().lower()
dashboard_variant = dbutils.widgets.get("dashboard_variant").strip()
workspace_reference_csv = dbutils.widgets.get("workspace_reference_csv").strip()
account_host = dbutils.widgets.get("account_host").strip()
account_id = dbutils.widgets.get("account_id").strip()
client_id = dbutils.widgets.get("client_id").strip()
client_secret = dbutils.widgets.get("client_secret").strip()

if not catalog or not schema:
    raise ValueError("Both catalog and schema must be set.")

current_workspace_only = workspace_scope in {"current", "current_workspace"}

if workspace_scope not in {"", "account", "all"} and not current_workspace_only:
    raise ValueError(
        f"workspace_scope must be 'account' or 'current'. Got: {workspace_scope}"
    )

resolved_current_workspace_id = None


def choose_warehouse_id() -> str:
    if warehouse_id:
        return warehouse_id

    warehouses = list(w.warehouses.list())
    if not warehouses:
        raise RuntimeError("No SQL warehouses found. Set warehouse_id explicitly.")

    serverless = [
        wh for wh in warehouses if getattr(wh, "enable_serverless_compute", False)
    ]
    selected = (serverless or warehouses)[0]
    print(f"Using SQL warehouse: {selected.name} ({selected.id})")
    return selected.id


resolved_warehouse_id = choose_warehouse_id()

try:
    spark.sql(f"USE CATALOG `{catalog}`")
except PySparkException as ex:
    if ex.getErrorClass() == "NO_SUCH_CATALOG_EXCEPTION":
        spark.sql(f"CREATE CATALOG IF NOT EXISTS `{catalog}`")
    else:
        raise

spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")

# COMMAND ----------


def _template_dir() -> Path:
    return Path(f"{_bundle_root()}/dashboard_templates")


def _variant_label() -> str:
    if dashboard_variant:
        return dashboard_variant
    if current_workspace_only:
        return "Current Workspace"
    return ""


def _safe_path_part(value: str) -> str:
    safe = "".join(char if char.isalnum() else "_" for char in value.lower())
    return "_".join(part for part in safe.split("_") if part)


def _dashboard_parent_path() -> str:
    variant = _variant_label()
    if not variant:
        return f"{_bundle_root()}/dashboards"
    return f"{_bundle_root()}/dashboards_{_safe_path_part(variant)}"


def _dashboard_name(template: Path) -> str:
    return template.name.removesuffix(".lvdash.json.tmpl")


def _dashboard_display_name(template: Path) -> str:
    variant = _variant_label()
    name = _dashboard_name(template)
    return f"{name} - {variant}" if variant else name


def _dashboard_workspace_path(template: Path) -> str:
    return f"{_dashboard_parent_path()}/{_dashboard_display_name(template)}.lvdash.json"


def _current_workspace_id() -> str:
    global resolved_current_workspace_id
    if resolved_current_workspace_id is None:
        resolved_current_workspace_id = str(w.get_workspace_id())
        print(f"Rendering dashboards for workspace_id={resolved_current_workspace_id}")
    return resolved_current_workspace_id


def _workspace_scoped_query(query: str) -> str:
    if not current_workspace_only:
        return query

    workspace_id = _current_workspace_id()
    scoped_tables = [
        "system.access.audit",
        "system.access.column_lineage",
        "system.access.table_lineage",
        "system.billing.usage",
        "system.compute.clusters",
        "system.compute.node_timeline",
        "system.compute.warehouse_events",
        "system.lakeflow.job_run_timeline",
        "system.lakeflow.job_task_run_timeline",
        "system.lakeflow.jobs",
        "system.query.history",
    ]

    for table_name in scoped_tables:
        query = query.replace(
            table_name,
            f"(SELECT * FROM {table_name} WHERE workspace_id = '{workspace_id}')",
        )
    return query


def _scope_dashboard_queries(value):
    if isinstance(value, dict):
        return {
            key: _workspace_scoped_query(item)
            if key == "query" and isinstance(item, str)
            else _scope_dashboard_queries(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_scope_dashboard_queries(item) for item in value]
    return value


def _render_workspace_scope(data: str) -> str:
    if not current_workspace_only:
        return data

    dashboard = json.loads(data)
    return json.dumps(_scope_dashboard_queries(dashboard), separators=(",", ":"))


def list_dashboard_templates() -> list[Path]:
    templates = sorted(_template_dir().glob("*.lvdash.json.tmpl"))
    if not templates:
        raise RuntimeError(f"No dashboard templates found in {_template_dir()}")
    print("Dashboard templates found:")
    for template in templates:
        print(f"  {template.name}")
    return templates


def rendered_dashboard(
    template: Path, dashboard_ids: dict[str, str] | None = None
) -> str:
    data = template.read_text()
    data = data.replace("{catalog}", f"`{catalog}`").replace("{schema}", f"`{schema}`")
    data = _render_workspace_scope(data)

    if dashboard_ids:
        host_url = f"https://{spark.conf.get('spark.databricks.workspaceUrl')}"
        for dash_name, dash_id in dashboard_ids.items():
            data = data.replace(
                f"**[{dash_name}](*)**",
                f"**[{dash_name}]({host_url}/dashboardsv3/{dash_id}/published)**",
            )
    return data


def existing_dashboard_id(template: Path) -> str | None:
    try:
        return w.workspace.get_status(_dashboard_workspace_path(template)).resource_id
    except Exception as exc:
        if "doesn't exist" in str(exc) or "RESOURCE_DOES_NOT_EXIST" in str(exc):
            return None
        raise


def deploy_dashboards() -> dict[str, str]:
    templates = list_dashboard_templates()
    parent_path = _dashboard_parent_path()
    w.workspace.mkdirs(parent_path)

    dashboard_ids: dict[str, str] = {}
    for template in templates:
        dash_name = _dashboard_name(template)
        display_name = _dashboard_display_name(template)
        dash_id = existing_dashboard_id(template)
        serialized = rendered_dashboard(template)

        if dash_id:
            current = w.lakeview.get(dash_id)
            current.display_name = display_name
            current.serialized_dashboard = serialized
            updated = w.lakeview.update(dashboard_id=dash_id, dashboard=current)
            print(f'Dashboard "{display_name}" updated at {updated.create_time}')
        else:
            created = w.lakeview.create(
                dashboard=Dashboard(
                    display_name=display_name,
                    parent_path=parent_path,
                    serialized_dashboard=serialized,
                    warehouse_id=resolved_warehouse_id,
                )
            )
            dash_id = created.dashboard_id
            print(f'Dashboard "{display_name}" created at {created.create_time}')

        dashboard_ids[dash_name] = dash_id

    update_index_dashboard_links(templates, dashboard_ids)
    return dashboard_ids


def update_index_dashboard_links(
    templates: list[Path], dashboard_ids: dict[str, str]
) -> None:
    for template in templates:
        if "Databricks Unified Cost Analysis" not in template.name:
            continue

        dash_id = existing_dashboard_id(template)
        if not dash_id:
            return

        current = w.lakeview.get(dash_id)
        current.serialized_dashboard = rendered_dashboard(template, dashboard_ids)
        updated = w.lakeview.update(dashboard_id=dash_id, dashboard=current)
        host_url = f"https://{spark.conf.get('spark.databricks.workspaceUrl')}"
        print(f"Index dashboard links updated at {updated.create_time}")
        print(f"{host_url}/dashboardsv3/{dash_id}/published")
        return


def publish_dashboards(dashboard_ids: dict[str, str] | None = None) -> None:
    ids = dashboard_ids or {
        _dashboard_name(template): existing_dashboard_id(template)
        for template in list_dashboard_templates()
    }

    for dash_name, dash_id in ids.items():
        if not dash_id:
            print(f'Dashboard "{dash_name}" does not exist, skipping publish')
            continue
        published = w.lakeview.publish(
            dashboard_id=dash_id,
            warehouse_id=resolved_warehouse_id,
        )
        print(f'Dashboard "{dash_name}" published at {published.revision_create_time}')
        grant_dashboard_read(dash_id)


def grant_dashboard_read(dashboard_id: str) -> None:
    if not dashboard_viewers_group:
        return

    try:
        w.permissions.set(
            request_object_type="dashboards",
            request_object_id=dashboard_id,
            access_control_list=[
                AccessControlRequest(
                    group_name=dashboard_viewers_group,
                    permission_level=PermissionLevel.CAN_READ,
                )
            ],
        )
        print(f"Granted CAN_READ on {dashboard_id} to {dashboard_viewers_group}")
    except Exception as exc:
        print(f"Could not grant dashboard permissions for {dashboard_id}: {exc}")


# COMMAND ----------


def create_sql_functions() -> None:
    function_prefix = f"`{catalog}`.`{schema}`"

    print(f"Creating {catalog}.{schema}.job_type_from_sku function...")
    spark.sql(
        f"""CREATE OR REPLACE FUNCTION {function_prefix}.job_type_from_sku(sku STRING)
          RETURNS STRING
          RETURN
          CASE
            WHEN sku LIKE '%JOBS_SERVERLESS%' THEN 'JOBS_SERVERLESS'
            WHEN sku LIKE '%JOBS_COMPUTE_(PHOTON)%' THEN 'JOBS_COMPUTE_PHOTON'
            WHEN sku LIKE '%JOBS_COMPUTE%' THEN 'JOBS_COMPUTE'
            WHEN sku IS NULL THEN 'UNKNOWN'
            ELSE 'OTHER'
          END;"""
    )

    print(f"Creating {catalog}.{schema}.sql_type_from_sku function...")
    spark.sql(
        f"""CREATE OR REPLACE FUNCTION {function_prefix}.sql_type_from_sku(sku STRING)
          RETURNS STRING
          RETURN
          CASE
            WHEN sku LIKE '%SERVERLESS_SQL%' THEN 'SQL_SERVERLESS'
            WHEN sku LIKE '%SQL_PRO%' THEN 'SQL_PRO'
            WHEN sku LIKE '%SQL%' THEN 'SQL_CLASSIC'
            WHEN sku IS NULL THEN 'UNKNOWN'
            ELSE 'OTHER'
          END;"""
    )

    print(f"Creating {catalog}.{schema}.team_name_from_tags function...")
    keys = [
        key.strip() for key in tags_to_consider_for_team_name.split(",") if key.strip()
    ]
    param_cols = ["cluster_tags", "job_tags"]
    case_list = []
    for param_col in param_cols:
        case_statement = "CASE\n"
        for key in keys:
            case_statement += (
                f"WHEN map_contains_key({param_col}, '{key}') "
                f"THEN lower({param_col}.`{key}`)\n"
            )
        case_statement += (
            f"WHEN map_contains_key({param_col}, 'LakehouseMonitoring') "
            f"AND {param_col}.LakehouseMonitoring = 'true' "
            "THEN 'LakehouseMonitoring'\n"
        )
        case_statement += f"ELSE NULL END AS {param_col}_team_name_init\n"
        case_list.append(case_statement)

    query = (
        "SELECT ifnull(cluster_tags_team_name_init, job_tags_team_name_init) "
        f"AS team_name_init FROM (SELECT {', '.join(case_list)})"
    )
    query = f"(SELECT ifnull(team_name_init, 'unknown') AS team_name FROM ({query}))"

    spark.sql(
        f"""CREATE OR REPLACE FUNCTION {function_prefix}.team_name_from_tags(
            cluster_tags MAP<STRING,STRING>,
            job_tags MAP<STRING,STRING>
        )
        RETURNS STRING RETURN {query}"""
    )
    print("SQL functions created successfully")


def create_update_tables() -> None:
    table_prefix = f"`{catalog}`.`{schema}`"

    print(f"Creating {catalog}.{schema}.workspace_reference table...")
    spark.sql(
        f"CREATE TABLE IF NOT EXISTS {table_prefix}.workspace_reference "
        "(workspace_id STRING, workspace_name STRING)"
    )

    def workspace_ref_with_usage_fallback(workspace_ref):
        workspace_ref.createOrReplaceTempView("workspace_ref")
        return spark.sql(
            """SELECT * FROM workspace_ref
            UNION
            SELECT DISTINCT workspace_id, workspace_id AS workspace_name
            FROM system.billing.usage
            WHERE workspace_id NOT IN (SELECT workspace_id FROM workspace_ref)"""
        )

    def load_workspace_ref_from_csv():
        if not workspace_reference_csv:
            return None

        csv_path = Path(workspace_reference_csv)
        if not csv_path.is_absolute():
            csv_path = Path(_bundle_root()) / csv_path

        if not csv_path.exists():
            print(f"No workspace reference CSV found at {csv_path}")
            return None

        workspace_names = {}
        with csv_path.open(newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            required_columns = {"workspace_id", "workspace_name"}
            if not required_columns.issubset(reader.fieldnames or []):
                raise ValueError(
                    f"{csv_path} must contain columns: workspace_id, workspace_name"
                )

            for row in reader:
                workspace_id = row["workspace_id"].strip()
                workspace_name = row["workspace_name"].strip()
                if not workspace_id or not workspace_name:
                    continue
                if (
                    workspace_id in workspace_names
                    and workspace_names[workspace_id] != workspace_name
                ):
                    raise ValueError(
                        f"{csv_path} has conflicting names for workspace_id "
                        f"{workspace_id}"
                    )
                workspace_names[workspace_id] = workspace_name

        rows = [
            {"workspace_id": workspace_id, "workspace_name": workspace_name}
            for workspace_id, workspace_name in sorted(workspace_names.items())
        ]

        if not rows:
            print(f"Workspace reference CSV is empty: {csv_path}")
            return None

        print(f"Using workspace names from CSV: {csv_path}")
        return spark.createDataFrame(rows, ["workspace_id", "workspace_name"])

    csv_workspace_ref = load_workspace_ref_from_csv()
    if csv_workspace_ref is not None:
        workspace_ref = workspace_ref_with_usage_fallback(csv_workspace_ref)
    else:
        try:
            if not (account_id and client_id and client_secret):
                raise ValueError("Account API credentials not supplied")

            a = AccountClient(
                host=account_host,
                account_id=account_id,
                client_id=client_id,
                client_secret=client_secret,
            )
            workspaces = [
                [workspace.workspace_id, workspace.workspace_name]
                for workspace in a.workspaces.list()
            ]
            workspace_ref = spark.createDataFrame(
                workspaces,
                ["workspace_id", "workspace_name"],
            )
            workspace_ref = workspace_ref.withColumn(
                "workspace_id",
                col("workspace_id").cast(StringType()),
            )
            workspace_ref = workspace_ref_with_usage_fallback(workspace_ref)
        except Exception as exc:
            print(f"Using workspace IDs as names in workspace_reference: {exc}")
            workspace_ref = spark.sql(
                f"""SELECT * FROM {table_prefix}.workspace_reference
                UNION
                SELECT DISTINCT workspace_id, workspace_id AS workspace_name
                FROM system.billing.usage
                WHERE workspace_id NOT IN (
                  SELECT workspace_id FROM {table_prefix}.workspace_reference
                )"""
            )

    workspace_ref.write.mode("overwrite").saveAsTable(
        f"{catalog}.{schema}.workspace_reference"
    )
    print(f"Table {catalog}.{schema}.workspace_reference created/updated")

    print(f"Creating {catalog}.{schema}.warehouse_reference table...")
    spark.sql(
        f"CREATE TABLE IF NOT EXISTS {table_prefix}.warehouse_reference "
        "(workspace_id STRING, warehouse_id STRING, warehouse_name STRING)"
    )

    warehouse_names = spark.sql(
        f"""WITH warehouse_names AS (
              SELECT
                workspace_id,
                GET_JSON_OBJECT(response.result, '$.id') AS warehouse_id,
                max(request_params.name) AS warehouse_name
              FROM system.access.audit
              WHERE service_name = 'databrickssql'
              GROUP BY workspace_id, GET_JSON_OBJECT(response.result, '$.id')
            ),
            union_warehouses AS (
              SELECT * FROM warehouse_names
              UNION
              SELECT * FROM {table_prefix}.warehouse_reference
            )
            SELECT * FROM union_warehouses"""
    )

    warehouse_names.write.mode("overwrite").saveAsTable(
        f"{catalog}.{schema}.warehouse_reference"
    )
    print(f"Table {catalog}.{schema}.warehouse_reference created/updated")


# COMMAND ----------


selected_actions = [action.strip() for action in actions.split(",") if action.strip()]
run_all = "All" in selected_actions
dashboard_ids = None

if run_all or "Create Functions" in selected_actions:
    create_sql_functions()

if run_all or "Create/refresh Tables" in selected_actions:
    create_update_tables()

if run_all or "Deploy Dashboards" in selected_actions:
    dashboard_ids = deploy_dashboards()

if run_all or "Publish Dashboards" in selected_actions:
    publish_dashboards(dashboard_ids)
