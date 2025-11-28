import os

from databricks.sdk.runtime import spark

from .transform import with_double


def main() -> None:
    """Entry point for the vscode-demo job (runs against Databricks serverless)."""
    df = spark.range(0, 10)
    df2 = with_double(df, col_name="double")

    target_table = os.getenv(
        "VSCODE_DEMO_TARGET_TABLE", "bronze_default.vscode_demo_result"
    )

    spark.sql(
        f"CREATE TABLE IF NOT EXISTS {target_table} "
        "(id BIGINT, double BIGINT) USING DELTA"
    )

    df2.write.mode("overwrite").format("delta").saveAsTable(target_table)

    print(f"Wrote {df2.count()} rows to {target_table}")
