# %%
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from vscode_demo.transform import with_double  # noqa: E402

# %%
if "spark" not in globals():
    try:
        from databricks.connect import DatabricksSession
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError(
            "Databricks Connect is required for local execution.\n"
            "Install and configure it (https://docs.databricks.com/dev-tools/databricks-connect.html),"
            " then re-run this notebook."
        ) from exc

    spark = DatabricksSession.builder.getOrCreate()

# %%
if "display" not in globals():

    def display(df):  # type: ignore[no-redef,func-assign]
        """Fallback display that just calls DataFrame.show()."""
        df.show(truncate=False)


# %%
df = spark.range(0, 5)

# %%
df2 = with_double(df, col_name="double")

# %%
display(df2)

# %%
print("Row count:", df2.count())
