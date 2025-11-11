# Databricks notebook source
# MAGIC %md
# MAGIC # Common Helpers
# MAGIC 
# MAGIC Reusable utilities shared across API ingestion notebooks.

# COMMAND ----------

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_CATALOG = "origo_felles_dev_green"
DEFAULT_SCHEMA = "api_ingest"
BRONZE_TABLE_NAME = "bronze_api_data"
DDL_RESTRICTED_CATALOGS = {DEFAULT_CATALOG}


def quote_identifier(identifier: str) -> str:
    """Return an ANSI SQL quoted identifier for Spark."""
    escaped = identifier.replace("`", "``")
    return f"`{escaped}`"


@dataclass(frozen=True)
class TableContext:
    """Resolved identifiers and names for a catalog / schema / table triple."""

    catalog: str
    schema: str
    table_name: str
    catalog_identifier: str
    schema_identifier: str
    table_identifier: str

    @property
    def table_fqn(self) -> str:
        """Fully-qualified table name without quoting."""
        return f"{self.catalog}.{self.schema}.{self.table_name}"

    @property
    def database_identifier(self) -> str:
        """Quoted catalog.schema identifier for SQL statements."""
        return f"{self.catalog_identifier}.{self.schema_identifier}"


def build_table_context(
    catalog: str,
    schema: str,
    table_name: str = BRONZE_TABLE_NAME,
) -> TableContext:
    """Build a `TableContext` with quoted identifiers for SQL usage."""
    catalog_identifier = quote_identifier(catalog)
    schema_identifier = quote_identifier(schema)
    table_identifier = (
        f"{catalog_identifier}.{schema_identifier}.{quote_identifier(table_name)}"
    )

    return TableContext(
        catalog=catalog,
        schema=schema,
        table_name=table_name,
        catalog_identifier=catalog_identifier,
        schema_identifier=schema_identifier,
        table_identifier=table_identifier,
    )


def allows_schema_ddl(catalog: str) -> bool:
    """
    Return True if notebooks should attempt to create catalogs/schemas automatically.

    Some shared catalogs (for example, DEFAULT_CATALOG) disallow CREATE CATALOG/SCHEMA
    statements for regular users. Skip DDL in those catalogs to avoid unnecessary retries.
    """
    return catalog not in DDL_RESTRICTED_CATALOGS
