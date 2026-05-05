# Draft script for making backups of Databricks tables
#
# Uses a table to track last beackup times and for configuring frequency

from datetime import datetime

from pyspark.sql import functions as sf


def updated_backup_schedule_table(backup_table_name):
    tables_df = spark.read.table("system.information_schema.tables").filter(
        "table_owner != 'System user'"
    )
    backup_df = None
    if spark.catalog.tableExists(backup_table_name):
        backup_df = spark.read.table(backup_table_name)
    else:
        from pyspark.sql.types import (
            IntegerType,
            StringType,
            StructField,
            StructType,
            TimestampType,
        )

        schema = StructType([
            StructField("catalog", StringType(), False),
            StructField("schema", StringType(), False),
            StructField("name", StringType(), False),
            StructField("backup_frequency_sec", IntegerType(), True),
            StructField("last_backup", TimestampType(), True),
        ])
        backup_df = spark.createDataFrame([], schema)
    new_backup_df = (
        tables_df
        .join(
            backup_df,
            backup_df.catalog == tables_df.table_catalog,
            backup_df.schema == tables_df.table_schema,
            backup_df.name == tables_df.table_name,
            "left_outer",
        )
        .select(
            sf.coalesce(backup_df.catalog, tables_df.table_catalog).alias("catalog"),
            sf.coalesce(backup_df.schema, tables_df.table_schema).alias("schema"),
            sf.coalesce(backup_df.name, tables_df.table_name).alias("name"),
            backup_df.backup_frequency_sec,
            backup_df.last_backup,
        )
        .checkpoint()
    )
    return new_backup_df


def do_backup(full_table_name):
    workspace = spark.conf.get("spark.databricks.workspaceUrl").split(".")[0]
    dir_path = (
        "s3://backup_place/information_schema/"
        + workspace
        + "/"
        + datetime.now().strftime("%Y-%m-%d_%H:%M")
    )
    file_name = full_table_name.replace(".", "_")
    file_path = dir_path + "/" + file_name
    spark.read.table(full_table_name).write.json(
        file_path, mode="overwrite", compression="gzip"
    )


backup_table_name = "ops.ops.table_backup_schedule"
backup_schedule_df = updated_backup_schedule_table(backup_table_name)
default_backup_frequency_sql = str(60 * 60 * 24)
needs_backup = backup_schedule_df.filter(
    "last_backup IS NULL OR timestamp_add('SECOND', COALESCE(backup_frequency_sec, "
    + default_backup_frequency_sql
    + "), last_backup) > current_timestamp()"
).collect()
for table in needs_backup:
    full_name = ".".join([table.catalog, table.schema, table.name])
    do_backup(full_name)
    backup_schedule_df = backup_schedule_df.withColumn(
        "last_backup",
        sf.when(
            backup_schedule_df.catalog
            == table.catalog & backup_schedule_df.schema
            == table.schema & backup_schedule_df.name
            == table.name,
            sf.current_timestamp(),
        ).otherwise(backup_schedule_df.last_backup),
    ).checkpoint()
    backup_schedule_df.write.mode("overwrite").saveAsTable(backup_table_name)
