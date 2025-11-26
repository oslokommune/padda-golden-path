"""Setup module for creating database schema and bronze table."""

import sys

from pyspark.sql import SparkSession

from api_ingest.common import (
    DEFAULT_CATALOG,
    DEFAULT_SCHEMA,
    allows_schema_ddl,
    build_table_context,
)


def get_spark() -> SparkSession:
    """Get or create Spark session."""
    return SparkSession.builder.getOrCreate()


def setup_schema(
    catalog: str = DEFAULT_CATALOG,
    schema: str = DEFAULT_SCHEMA,
    spark: SparkSession | None = None,
) -> None:
    """
    Set up database schema and bronze table for API ingestion.

    Args:
        catalog: The catalog name
        schema: The schema/database name
        spark: Optional Spark session (will create one if not provided)
    """
    if spark is None:
        spark = get_spark()

    bronze_context = build_table_context(catalog, schema)
    bronze_table = bronze_context.table_fqn
    bronze_table_identifier = bronze_context.table_identifier
    can_manage_schema = allows_schema_ddl(catalog)

    # Create catalog (skip DDL inside shared catalogs we cannot manage)
    if can_manage_schema:
        spark.sql(f"CREATE CATALOG IF NOT EXISTS {bronze_context.catalog_identifier}")
        print(f"✅ Created/verified catalog: {catalog}")
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
        print(f"✅ Created/verified schema: {catalog}.{schema}")
    else:
        print(
            f"ℹ️ Skipping schema creation in managed catalog '{catalog}'. "
            f"Expecting schema '{schema}' to be provisioned up-front."
        )

    # Create bronze table to store raw API responses
    spark.sql(
        f"""CREATE TABLE IF NOT EXISTS {bronze_table_identifier} (
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

    print(f"✅ Created/verified table: {bronze_table}")

    # Verify tables exist
    tables = spark.sql(f"SHOW TABLES IN {bronze_context.database_identifier}").collect()
    print(f"\n📊 Tables in {catalog}.{schema}:")
    for table in tables:
        print(f"  - {table.tableName}")


def main() -> None:
    """Main entry point for setup task."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup API ingestion schema and tables"
    )
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

    args = parser.parse_args()

    try:
        setup_schema(catalog=args.catalog, schema=args.schema)
        print("\n✅ Setup completed successfully")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
