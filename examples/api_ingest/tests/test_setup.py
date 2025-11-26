"""Tests for the setup module."""

from __future__ import annotations

from unittest.mock import Mock

from api_ingest import setup


def _mock_spark_session() -> Mock:
    spark = Mock()

    def sql_effect(query: str):
        if query.startswith("SHOW TABLES"):
            result = Mock()
            result.collect.return_value = [Mock(tableName="bronze_api_data")]
            return result
        return Mock()

    spark.sql.side_effect = sql_effect
    return spark


def test_setup_schema_runs_catalog_and_schema_ddls(monkeypatch):
    """Ensure schema creation runs when DDL is allowed."""

    spark = _mock_spark_session()
    monkeypatch.setattr(setup, "allows_schema_ddl", lambda _catalog: True)

    setup.setup_schema(catalog="demo_catalog", schema="demo_schema", spark=spark)

    executed_sql = [call.args[0] for call in spark.sql.call_args_list]

    print("Executed SQL statements:")
    for stmt in executed_sql:
        print(stmt)
    print("Catalog")
    assert any(stmt.startswith("CREATE CATALOG") for stmt in executed_sql)
    print("Schema")
    assert any(stmt.startswith("CREATE SCHEMA") for stmt in executed_sql)
    print("Table")
    assert any(stmt.startswith("CREATE TABLE") for stmt in executed_sql)
    print("Show Tables")
    assert any(stmt.startswith("SHOW TABLES") for stmt in executed_sql)


def test_setup_schema_skips_catalog_when_restricted(monkeypatch):
    """Ensure catalog/schema DDL is skipped when not allowed."""

    spark = _mock_spark_session()
    monkeypatch.setattr(setup, "allows_schema_ddl", lambda _catalog: False)

    setup.setup_schema(catalog="restricted", schema="bronze", spark=spark)

    executed_sql = [call.args[0] for call in spark.sql.call_args_list]

    assert not any(stmt.startswith("CREATE CATALOG") for stmt in executed_sql)
    assert not any(stmt.startswith("CREATE SCHEMA") for stmt in executed_sql)
    assert any(stmt.startswith("CREATE TABLE") for stmt in executed_sql)
    assert any(stmt.startswith("SHOW TABLES") for stmt in executed_sql)
