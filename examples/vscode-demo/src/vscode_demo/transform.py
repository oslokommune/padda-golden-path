from pyspark.sql import DataFrame, functions as F


def with_double(df: DataFrame, *, col_name: str = "value") -> DataFrame:
    """Return DataFrame with an extra column that doubles the input id.

    Args:
        df: Input Spark DataFrame with a column `id`.
        col_name: Name of the new column to create.

    Returns:
        DataFrame with new column containing `id * 2`.
    """
    return df.withColumn(col_name, F.col("id") * F.lit(2))
