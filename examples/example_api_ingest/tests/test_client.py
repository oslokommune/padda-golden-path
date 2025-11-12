from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest
import requests
from api_ingest.client import APIClient


def test_fetch_success(monkeypatch: pytest.MonkeyPatch) -> None:
    client = APIClient("https://example.com", max_retries=1)

    response_mock = Mock()
    response_mock.json.return_value = {"status": "ok"}
    response_mock.status_code = 200
    response_mock.raise_for_status = Mock()

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, Any] | None,
        timeout: int,
    ) -> Mock:
        assert url == "https://example.com/resource"
        assert headers["Content-Type"] == "application/json"
        assert timeout == client.timeout
        return response_mock

    monkeypatch.setattr(requests, "get", fake_get)

    result = client.fetch("/resource")

    assert result["success"] is True
    assert result["status_code"] == 200
    assert result["data"] == {"status": "ok"}
    assert result["url"].endswith("/resource")


def test_fetch_failure_after_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    client = APIClient("https://example.com", max_retries=2)

    attempt_tracker = {"count": 0}
    error_response = Mock(status_code=503)

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, Any] | None,
        timeout: int,
    ) -> Mock:
        attempt_tracker["count"] += 1
        exc = requests.exceptions.HTTPError("service unavailable")
        exc.response = error_response
        raise exc

    monkeypatch.setattr(requests, "get", fake_get)

    result = client.fetch("/unstable")

    assert attempt_tracker["count"] == client.max_retries
    assert result["success"] is False
    assert result["status_code"] == 503
    assert "service unavailable" in result["error"]


def test_fetch_paginated_accumulates_results(monkeypatch: pytest.MonkeyPatch) -> None:
    client = APIClient("https://example.com")
    calls: list[int] = []

    def fake_fetch(
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        page = params["page"]
        calls.append(page)
        if page < 3:
            return {
                "success": True,
                "data": [{"page": page}],
                "status_code": 200,
                "url": f"https://example.com{endpoint}",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        return {
            "success": True,
            "data": [],
            "status_code": 200,
            "url": f"https://example.com{endpoint}",
            "timestamp": "2024-01-01T00:00:00Z",
        }

    monkeypatch.setattr(client, "fetch", fake_fetch)

    result = client.fetch_paginated("/items", per_page=10, max_pages=5)

    assert result["success"] is True
    assert result["total_records"] == 2
    assert calls == [1, 2, 3]
    assert result["data"] == [{"page": 1}, {"page": 2}]
