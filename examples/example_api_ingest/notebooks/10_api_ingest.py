from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from typing import Any

import requests
from _common import (  # type: ignore[import-not-found]
    DEFAULT_CATALOG,
    DEFAULT_SCHEMA,
    build_table_context,
    dbutils,
    display,
    spark,
)

# Databricks notebook source
# MAGIC %md
# MAGIC # API Ingestion: Fetch and Store Data from API
# MAGIC
# MAGIC This notebook demonstrates how to:
# MAGIC 1. Fetch data from an external API
# MAGIC 2. Store raw API responses in the bronze layer
# MAGIC 3. Handle errors and retries

# COMMAND ----------

# MAGIC %md
# MAGIC ## Parameters

# COMMAND ----------

# MAGIC %run ./_common

# COMMAND ----------

dbutils.widgets.text("catalog", DEFAULT_CATALOG, "Catalog")
dbutils.widgets.text("schema", DEFAULT_SCHEMA, "Schema")
dbutils.widgets.text(
    "api_base_url",
    "https://test.io.web.oslo.kommune.no",
    "API Base URL",
)
dbutils.widgets.text("api_endpoint", "/v3/salaries/current", "API Endpoint")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
api_base_url = dbutils.widgets.get("api_base_url")
api_endpoint = dbutils.widgets.get("api_endpoint")

bronze_context = build_table_context(catalog, schema)
bronze_table = bronze_context.table_fqn
bronze_table_identifier = bronze_context.table_identifier

# COMMAND ----------

# MAGIC %md
# MAGIC ## API Client Function

# COMMAND ----------


def fetch_api_data(
    base_url: str,
    endpoint: str,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = 5,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Fetch data from API with retry logic."""

    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    merged_headers = headers or {"Content-Type": "application/json"}

    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}: Fetching from {url}")

            response = requests.get(
                url,
                headers=merged_headers,
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()

            return {
                "data": response.json(),
                "status_code": response.status_code,
                "url": url,
                "timestamp": _current_timestamp(),
                "success": True,
            }

        except requests.exceptions.RequestException as exc:
            print(f"❌ Attempt {attempt + 1} failed: {exc}")
            if attempt == max_retries - 1:
                return {
                    "data": None,
                    "status_code": getattr(exc.response, "status_code", None)
                    if hasattr(exc, "response")
                    else None,
                    "url": url,
                    "timestamp": _current_timestamp(),
                    "error": str(exc),
                    "success": False,
                }
            time.sleep(2**attempt)  # Exponential backoff

    return {
        "data": None,
        "status_code": None,
        "url": url,
        "timestamp": _current_timestamp(),
        "error": "Max retries exceeded",
        "success": False,
    }


def _current_timestamp() -> str:
    """Return an ISO formatted UTC timestamp."""

    return datetime.now(UTC).isoformat()


# COMMAND ----------

# MAGIC %md
# MAGIC ## Fetch Data from API

# COMMAND ----------


print("📡 Fetching data from API...")
print(f"   Base URL: {api_base_url}")
print(f"   Endpoint: {api_endpoint}")

api_response = fetch_api_data(
    base_url=api_base_url,
    endpoint=api_endpoint,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Store Data in Bronze Layer

# COMMAND ----------


def _write_records(payload: list[dict[str, Any]]) -> None:
    """Helper to append records to the bronze table."""

    if spark is None:
        raise RuntimeError("Spark session is not available.")

    dataframe = spark.createDataFrame(payload)
    dataframe.write.format("delta").mode("append").saveAsTable(bronze_table)


if api_response["success"]:
    # Convert response data to JSON string
    response_json = json.dumps(api_response["data"])

    # Prepare metadata
    metadata = {
        "url": api_response["url"],
        "timestamp": api_response["timestamp"],
        "status_code": str(api_response["status_code"]),
    }

    # Create DataFrame with the API response
    rows = [
        {
            "ingestion_timestamp": datetime.now(UTC),
            "api_endpoint": api_endpoint,
            "response_data": response_json,
            "status_code": api_response["status_code"],
            "metadata": metadata,
        }
    ]

    _write_records(rows)

    record_count = (
        len(api_response["data"]) if isinstance(api_response["data"], list) else 1
    )
    print(
        f"✅ Successfully ingested {record_count} record(s) to {bronze_table}",
    )

    # Display sample of ingested data
    print("\n📋 Sample of ingested data:")
    display(
        spark.sql(  # type: ignore[union-attr]
            "SELECT * FROM "
            f"{bronze_table_identifier} "
            "ORDER BY ingestion_timestamp DESC LIMIT 5"
        )
    )

else:
    error_message = api_response.get("error", "Unknown error")
    print(f"❌ Failed to fetch data from API: {error_message}")

    error_rows = [
        {
            "ingestion_timestamp": datetime.now(UTC),
            "api_endpoint": api_endpoint,
            "response_data": None,
            "status_code": api_response.get("status_code"),
            "metadata": {
                "url": api_response["url"],
                "timestamp": api_response["timestamp"],
                "error": error_message,
            },
        }
    ]

    _write_records(error_rows)
    raise Exception(f"API ingestion failed: {error_message}")  # noqa: TRY002

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Statistics

# COMMAND ----------


if spark is None:
    raise RuntimeError("Spark session is not available.")

stats = spark.sql(
    f"""
SELECT
    COUNT(*) as total_records,
    MAX(ingestion_timestamp) as latest_ingestion,
    COUNT(DISTINCT api_endpoint) as unique_endpoints
FROM {bronze_table_identifier}
"""
).collect()[0]

print("\n📊 Ingestion Statistics:")
print(f"   Total records: {stats.total_records}")
print(f"   Latest ingestion: {stats.latest_ingestion}")
print(f"   Unique endpoints: {stats.unique_endpoints}")
