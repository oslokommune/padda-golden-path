from vscode_demo.transform import with_double


def test_with_double_creates_column(spark):
    df = spark.range(0, 3)

    result = with_double(df, col_name="double")

    rows = [r.double for r in result.orderBy("id").collect()]
    assert rows == [0, 2, 4]
