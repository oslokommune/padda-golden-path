from __future__ import annotations

from _common import (  # type: ignore[import-not-found]
    DEFAULT_CATALOG,
    DEFAULT_SCHEMA,
    allows_schema_ddl,
    build_table_context,
    dbutils,
    spark,
)

# Databricks notebook source
# MAGIC %md
# MAGIC # Setup: Create Database Schema
# MAGIC
# MAGIC This notebook sets up the database schema for API ingestion.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Parameters
# MAGIC
# MAGIC - `catalog`: The catalog name (default: origo_felles_dev_green)
# MAGIC - `schema`: The schema/database name (default: api_ingest)

# COMMAND ----------

# MAGIC %run ./_common

# COMMAND ----------

dbutils.widgets.text("catalog", DEFAULT_CATALOG, "Catalog")
dbutils.widgets.text("schema", DEFAULT_SCHEMA, "Schema")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

bronze_context = build_table_context(catalog, schema)
bronze_table = bronze_context.table_fqn
bronze_table_identifier = bronze_context.table_identifier
can_manage_schema = allows_schema_ddl(catalog)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Catalog and Schema

# COMMAND ----------

# Create catalog (skip DDL inside shared catalogs we cannot manage)
if can_manage_schema:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {bronze_context.catalog_identifier}")
else:
    print(
        f"ℹ️ Skipping catalog creation in managed catalog '{catalog}'. "
        "Ensure it already exists or request access."
    )

# Create schema for catalogs we control
if can_manage_schema:
    spark.sql(
        f"CREATE SCHEMA IF NOT EXISTS {bronze_context.catalog_identifier}."
        f"{bronze_context.schema_identifier}"
    )
else:
    print(
        f"ℹ️ Skipping schema creation in managed catalog '{catalog}'. "
        f"Expecting schema '{schema}' to be provisioned up-front."
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Bronze Table for Raw API Data

# COMMAND ----------

# Create bronze table to store raw API responses
spark.sql(
    f"""
CREATE TABLE IF NOT EXISTS {bronze_table_identifier} (
    ingestion_timestamp TIMESTAMP,
    api_endpoint STRING,
    response_data STRING,
    status_code INT,
    metadata MAP<STRING, STRING>
)
USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
"""
)

print(f"✅ Created table: {bronze_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Setup

# COMMAND ----------

# Verify tables exist
tables = spark.sql(f"SHOW TABLES IN {bronze_context.database_identifier}").collect()
print(f"\n📊 Tables in {catalog}.{schema}:")
for table in tables:
    print(f"  - {table.tableName}")
