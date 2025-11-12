"""Tests for API ingestion module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from api_ingest import ingest


def test_fetch_api_data_success() -> None:
    """Test successful API data fetch."""
    with patch("api_ingest.ingest.APIClient") as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.fetch.return_value = {
            "data": {"status": "ok"},
            "status_code": 200,
            "url": "https://example.com/api",
            "timestamp": "2024-01-01T00:00:00Z",
            "success": True,
        }

        result = ingest.fetch_api_data(
            base_url="https://example.com",
            endpoint="/api",
        )

        assert result["success"] is True
        assert result["status_code"] == 200
        mock_client.fetch.assert_called_once_with("/api", headers=None, params=None)


def test_ingest_api_data_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test successful API ingestion."""
    spark_mock = Mock()
    spark_session_mock = Mock()
    spark_session_mock.builder.getOrCreate.return_value = spark_mock

    monkeypatch.setattr("api_ingest.ingest.SparkSession", spark_session_mock)

    with patch("api_ingest.ingest.fetch_api_data") as mock_fetch:
        mock_fetch.return_value = {
            "data": {"items": [{"id": 1}]},
            "status_code": 200,
            "url": "https://example.com/api",
            "timestamp": "2024-01-01T00:00:00Z",
            "success": True,
        }

        df_mock = Mock()
        spark_mock.createDataFrame.return_value = df_mock
        spark_mock.sql.return_value.collect.return_value = [
            Mock(total_records=1, latest_ingestion="2024-01-01", unique_endpoints=1)
        ]

        ingest.ingest_api_data(
            catalog="test_catalog",
            schema="test_schema",
            api_base_url="https://example.com",
            api_endpoint="/api",
            spark=spark_mock,
        )

        df_mock.write.format.assert_called_once_with("delta")
        df_mock.write.format.return_value.mode.assert_called_once_with("append")
        df_mock.write.format.return_value.mode.return_value.saveAsTable.assert_called_once()


def test_ingest_api_data_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test API ingestion failure handling."""
    spark_mock = Mock()
    spark_session_mock = Mock()
    spark_session_mock.builder.getOrCreate.return_value = spark_mock

    monkeypatch.setattr("api_ingest.ingest.SparkSession", spark_session_mock)

    with patch("api_ingest.ingest.fetch_api_data") as mock_fetch:
        mock_fetch.return_value = {
            "data": None,
            "status_code": 500,
            "url": "https://example.com/api",
            "timestamp": "2024-01-01T00:00:00Z",
            "error": "Internal Server Error",
            "success": False,
        }

        df_mock = Mock()
        spark_mock.createDataFrame.return_value = df_mock

        with pytest.raises(Exception, match="API ingestion failed"):
            ingest.ingest_api_data(
                catalog="test_catalog",
                schema="test_schema",
                api_base_url="https://example.com",
                api_endpoint="/api",
                spark=spark_mock,
            )

        # Should still write error record
        df_mock.write.format.assert_called_once_with("delta")
