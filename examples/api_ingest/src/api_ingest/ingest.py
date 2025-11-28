"""API ingestion module for fetching and storing data from external APIs."""

import json
import sys
from datetime import UTC, datetime
from typing import Any

from pyspark.sql import SparkSession

from api_ingest.client import APIClient
from api_ingest.common import DEFAULT_CATALOG, DEFAULT_SCHEMA, build_table_context


def get_spark() -> SparkSession:
    """Get or create Spark session."""
    return SparkSession.builder.getOrCreate()


def fetch_api_data(
    base_url: str,
    endpoint: str,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = 30,
    max_retries: int = 3,
) -> dict[str, Any]:
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
    client = APIClient(base_url=base_url, timeout=timeout, max_retries=max_retries)
    return client.fetch(endpoint, headers=headers, params=params)


def ingest_api_data(
    catalog: str,
    schema: str,
    api_base_url: str,
    api_endpoint: str,
    spark: SparkSession | None = None,
) -> None:
    """
    Fetch data from API and store in bronze table.

    Args:
        catalog: The catalog name
        schema: The schema/database name
        api_base_url: Base URL of the API
        api_endpoint: API endpoint path
        spark: Optional Spark session (will create one if not provided)
    """
    if spark is None:
        spark = get_spark()

    bronze_context = build_table_context(catalog, schema)
    bronze_table = bronze_context.table_fqn
    bronze_table_identifier = bronze_context.table_identifier

    print("📡 Fetching data from API...")
    print(f"   Base URL: {api_base_url}")
    print(f"   Endpoint: {api_endpoint}")

    api_response = fetch_api_data(
        base_url=api_base_url,
        endpoint=api_endpoint,
    )

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
                "ingestion_timestamp": _current_timestamp(),
                "api_endpoint": api_endpoint,
                "response_data": response_json,
                "status_code": api_response["status_code"],
                "metadata": metadata,
            }
        ]

        df = spark.createDataFrame(data)

        # Write to bronze table
        df.write.format("delta").mode("append").saveAsTable(bronze_table)

        record_count = (
            len(api_response["data"]) if isinstance(api_response["data"], list) else 1
        )
        print(f"✅ Successfully ingested {record_count} record(s) to {bronze_table}")

        # Display sample of ingested data
        print("\n📋 Sample of ingested data:")
        sample_df = spark.sql(
            f"SELECT * FROM {bronze_table_identifier} "
            f"ORDER BY ingestion_timestamp DESC LIMIT 5"
        )
        sample_df.show(truncate=False)

    else:
        error_msg = api_response.get("error", "Unknown error")
        print(f"❌ Failed to fetch data from API: {error_msg}")

        # Store error information for debugging
        error_data = [
            {
                "ingestion_timestamp": _current_timestamp(),
                "api_endpoint": api_endpoint,
                "response_data": None,
                "status_code": api_response.get("status_code"),
                "metadata": {
                    "url": api_response["url"],
                    "timestamp": api_response["timestamp"],
                    "error": error_msg,
                },
            }
        ]

        df = spark.createDataFrame(error_data)
        df.write.format("delta").mode("append").saveAsTable(bronze_table)

        raise Exception(f"API ingestion failed: {error_msg}")

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

    print("\n📊 Ingestion Statistics:")
    print(f"   Total records: {stats.total_records}")
    print(f"   Latest ingestion: {stats.latest_ingestion}")
    print(f"   Unique endpoints: {stats.unique_endpoints}")


def _current_timestamp() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(UTC)


def main() -> None:
    """Main entry point for ingestion task."""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest data from external API")
    parser.add_argument(
        "--catalog",
        type=str,
        default=DEFAULT_CATALOG,
        help=f"Catalog name (default: {DEFAULT_CATALOG})",
    )
    parser.add_argument(
        "--schema",
        type=str,
        default=DEFAULT_SCHEMA,
        help=f"Schema name (default: {DEFAULT_SCHEMA})",
    )
    parser.add_argument(
        "--api-base-url",
        type=str,
        required=True,
        help="Base URL of the API",
    )
    parser.add_argument(
        "--api-endpoint",
        type=str,
        required=True,
        help="API endpoint path",
    )

    args = parser.parse_args()

    try:
        ingest_api_data(
            catalog=args.catalog,
            schema=args.schema,
            api_base_url=args.api_base_url,
            api_endpoint=args.api_endpoint,
        )
        print("\n✅ Ingestion completed successfully")
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
