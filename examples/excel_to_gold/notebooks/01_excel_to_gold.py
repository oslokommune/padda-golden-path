import importlib
import os
import re
import subprocess
import sys
import tempfile
import uuid
from typing import Any

import pandas as pd
from pyspark.sql import functions as F

# Hint to ruff: these names are provided by the Databricks runtime.
spark: Any = None
dbutils: Any = None
display: Any = None

# Databricks notebook source
# COMMAND ----------

dbutils.widgets.text("catalog", "padda_catalog_1234567890123456")
dbutils.widgets.text("schema", "wheels")
dbutils.widgets.text("table_name", "excel_gold")
dbutils.widgets.text(
    "excel_input_path",
    "dbfs:/Volumes/padda_catalog_1234567890123456/wheels/deps/exceltest-fil.xlsx",
)
dbutils.widgets.text(
    "openpyxl_whl_path",
    (
        "dbfs:/Volumes/padda_catalog_1234567890123456/wheels/deps/"
        "openpyxl-3.1.5-py2.py3-none-any.whl"
    ),
)
dbutils.widgets.text(
    "et_xmlfile_whl_path",
    (
        "dbfs:/Volumes/padda_catalog_1234567890123456/wheels/deps/"
        "et_xmlfile-2.0.0-py3-none-any.whl"
    ),
)

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
table_name = dbutils.widgets.get("table_name")
excel_input_path = dbutils.widgets.get("excel_input_path")
openpyxl_whl_path = dbutils.widgets.get("openpyxl_whl_path")
et_xmlfile_whl_path = dbutils.widgets.get("et_xmlfile_whl_path")

# COMMAND ----------


def to_local_volume_path(path: str) -> str:
    """Map UC Volume path to local driver path; avoids dbutils.fs copy."""
    if path.startswith("dbfs:/Volumes/"):
        return path.replace("dbfs:/Volumes/", "/Volumes/", 1)
    if path.startswith("/Volumes/"):
        return path
    raise ValueError(
        "excel_input_path must be a UC Volume path: dbfs:/Volumes/... or /Volumes/..."
    )


local_path = to_local_volume_path(excel_input_path)
local_whls = [
    to_local_volume_path(et_xmlfile_whl_path),
    to_local_volume_path(openpyxl_whl_path),
]

extra_lib_dir = tempfile.mkdtemp(prefix="openpyxl_whl_")

# Install wheels on the driver without internet (points to Volume paths).
for whl in local_whls:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--target",
            extra_lib_dir,
            whl,
        ],
    )
if extra_lib_dir not in sys.path:
    sys.path.insert(0, extra_lib_dir)

importlib.invalidate_caches()

if not os.path.exists(local_path):
    raise FileNotFoundError(
        f"Finner ikke Excel-fil på {local_path}. "
        "Sjekk at filen er lastet opp til Volume og at excel_input_path peker riktig."
    )

pdf = pd.read_excel(local_path, engine="openpyxl")

if pdf.empty:
    raise ValueError(f"Excel input was empty at path: {excel_input_path}")

# Clean column names for Delta compatibility.
sanitized_cols = []
seen = set()
for idx, col in enumerate(pdf.columns):
    # Replace whitespace and Delta-disallowed punctuation with underscores.
    base = re.sub(r"[\s,;{}()\n\t=]", "_", str(col).strip())
    base = re.sub("_+", "_", base).strip("_")
    if not base:
        base = f"col_{idx + 1}"
    candidate = base
    suffix = 1
    while candidate in seen:
        candidate = f"{base}_{suffix}"
        suffix += 1
    seen.add(candidate)
    sanitized_cols.append(candidate)
pdf.columns = sanitized_cols

ingest_run_id = str(uuid.uuid4())

try:
    spark.sql(f"USE CATALOG {catalog}")
except Exception as exc:
    raise RuntimeError(
        f"Katalogen '{catalog}' finnes ikke eller er utilgjengelig. "
        "Pek til en eksisterende katalog før du kjører jobben."
    ) from exc
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")

df = spark.createDataFrame(pdf)
df = (
    df.withColumn("_ingest_timestamp", F.current_timestamp())
    .withColumn("_ingest_source_path", F.lit(excel_input_path))
    .withColumn("_ingest_run_id", F.lit(ingest_run_id))
)

expectation_results = []
data_cols = [c for c in df.columns if not c.startswith("_")]
if data_cols:
    non_empty_expr = (
        F.greatest(*[F.col(c).isNotNull().cast("int") for c in data_cols]) == 1
    )
    total_rows = df.count()
    df = df.filter(non_empty_expr)
    kept_rows = df.count()
    failed_rows = total_rows - kept_rows
    expectation_results.append({
        "name": "drop_all_null_rows",
        "total_rows": total_rows,
        "failed_rows": failed_rows,
    })

if df.rdd.isEmpty():
    raise ValueError("Expectations failed: ingen rader igjen etter filtrering.")

df.write.format("delta").mode("overwrite").saveAsTable(
    f"{catalog}.{schema}.{table_name}"
)

display(spark.table(f"{catalog}.{schema}.{table_name}"))
if expectation_results:
    display(spark.createDataFrame(expectation_results))
