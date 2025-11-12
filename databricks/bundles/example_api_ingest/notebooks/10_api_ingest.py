# Databricks notebook source
# MAGIC %md
# MAGIC # API Ingestion: Fetch and Store Data from API
# MAGIC 
# MAGIC This notebook demonstrates how to:
# MAGIC 1. Fetch data from an external API
# MAGIC 2. Store raw API responses in bronze layer
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
    "api_base_url", "https://test.io.web.oslo.kommune.no", "API Base URL"
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
# MAGIC ## Import Libraries

# COMMAND ----------

import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# COMMAND ----------

# MAGIC %md
# MAGIC ## API Client Function

# COMMAND ----------

def fetch_api_data(
    base_url: str,
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 5,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    Fetch data from API with retry logic.
    
    Args:
        base_url: Base URL of the API
        endpoint: API endpoint path
        headers: Optional HTTP headers
        params: Optional query parameters
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    
    Returns:
        Dictionary containing response data, status code, and metadata
    """
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    if headers is None:
        headers = {"Content-Type": "application/json"}

    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}: Fetching from {url}")

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout,
            )

            response.raise_for_status()

            return {
                "data": response.json(),
                "status_code": response.status_code,
                "url": url,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
            }

        except requests.exceptions.RequestException as e:
            print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                return {
                    "data": None,
                    "status_code": getattr(e.response, "status_code", None)
                    if hasattr(e, "response")
                    else None,
                    "url": url,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e),
                    "success": False,
                }
            time.sleep(2**attempt)  # Exponential backoff

    return {
        "data": None,
        "status_code": None,
        "url": url,
        "timestamp": datetime.utcnow().isoformat(),
        "error": "Max retries exceeded",
        "success": False,
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Fetch Data from API

# COMMAND ----------

print(f"📡 Fetching data from API...")
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
    data = [
        {
            "ingestion_timestamp": datetime.utcnow(),
            "api_endpoint": api_endpoint,
            "response_data": response_json,
            "status_code": api_response["status_code"],
            "metadata": metadata,
        }
    ]

    df = spark.createDataFrame(data)

    # Write to bronze table
    df.write.format("delta").mode("append").saveAsTable(bronze_table)

    print(
        "✅ Successfully ingested"
        f" {len(api_response['data']) if isinstance(api_response['data'], list) else 1}"
        f" record(s) to {bronze_table}"
    )

    # Display sample of ingested data
    print("\n📋 Sample of ingested data:")
    display(
        spark.sql(
            f"SELECT * FROM {bronze_table_identifier} ORDER BY ingestion_timestamp DESC LIMIT 5"
        )
    )

else:
    print(f"❌ Failed to fetch data from API: {api_response.get('error', 'Unknown error')}")

    # Store error information for debugging
    error_data = [
        {
            "ingestion_timestamp": datetime.utcnow(),
            "api_endpoint": api_endpoint,
            "response_data": None,
            "status_code": api_response.get("status_code"),
            "metadata": {
                "url": api_response["url"],
                "timestamp": api_response["timestamp"],
                "error": api_response.get("error", "Unknown error"),
            },
        }
    ]

    df = spark.createDataFrame(error_data)
    df.write.format("delta").mode("append").saveAsTable(bronze_table)

    raise Exception(f"API ingestion failed: {api_response.get('error', 'Unknown error')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Statistics

# COMMAND ----------

# Get ingestion statistics
stats = spark.sql(
    f"""
SELECT 
    COUNT(*) as total_records,
    MAX(ingestion_timestamp) as latest_ingestion,
    COUNT(DISTINCT api_endpoint) as unique_endpoints
FROM {bronze_table_identifier}
"""
).collect()[0]

print(f"\n📊 Ingestion Statistics:")
print(f"   Total records: {stats.total_records}")
print(f"   Latest ingestion: {stats.latest_ingestion}")
print(f"   Unique endpoints: {stats.unique_endpoints}")
