# Databricks notebook source
# MAGIC %md
# MAGIC **Functionality:** Initializes the setup and configuration of the **Security Analysis Tool (SAT)**.
# MAGIC

# COMMAND ----------

# MAGIC %run ./diagnosis/pre_run_config_check

# COMMAND ----------

# MAGIC %run ./Includes/install_sat_sdk

# COMMAND ----------

# MAGIC %run ./Utils/initialize

# COMMAND ----------

# MAGIC %run ./Utils/common

# COMMAND ----------

hostname = (
    dbutils.notebook.entry_point.getDbutils()
    .notebook()
    .getContext()
    .apiUrl()
    .getOrElse(None)
)
cloud_type = getCloudType(hostname)

# COMMAND ----------

def run_notebook(notebook_path, timeout, required=True):
    try:
        status = dbutils.notebook.run(notebook_path, timeout)
        if status != "OK":
            msg = f"Error in {notebook_path}: {status}"
            if required:
                raise Exception(msg)
            loggr.warning(msg)
    except Exception as e:
        if required:
            raise
        loggr.warning(f"Optional step failed: {notebook_path} — {e}")

# COMMAND ----------

# Steps 1 (list_account_workspaces) and 3 (test_connections) require the
# Accounts API which is unreachable in SRA/isolated-network environments.
# Workspace config is derived from the runtime context at deploy time instead.
#
# Steps 4 and 9 are required (load config into tables).
# Steps 5 (dashboard) and 6 (alerts) are optional — they need a SQL warehouse
# and will be retried on next run if they fail.
notebooks = [
    ("4. enable_workspaces_for_sat", 3000, True),
    ("5. import_dashboard_template_lakeview", 3000, False),
    ("6. configure_alerts_template", 3000, False),
    ("9. self_assess_workspace_configuration", 3000, True),
]

for notebook, timeout, required in notebooks:
    run_notebook(f"{basePath()}/notebooks/Setup/{notebook}", timeout, required)

# COMMAND ----------

spark.sql(f"DROP DATABASE IF EXISTS {json_['intermediate_schema']} CASCADE")