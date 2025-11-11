"""API client for fetching data from external APIs."""

import time
from datetime import UTC, datetime
from typing import Any

import requests


class APIClient:
    """Client for fetching data from REST APIs with retry logic."""

    def __init__(
        self,
        base_url: str,
        default_headers: dict[str, str] | None = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize API client.

        Args:
            base_url: Base URL of the API
            default_headers: Default HTTP headers to include in requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers: dict[str, str] = default_headers or {
            "Content-Type": "application/json"
        }
        self.timeout = timeout
        self.max_retries = max_retries

    def fetch(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Fetch data from API endpoint with retry logic.

        Args:
            endpoint: API endpoint path
            headers: Optional HTTP headers (merged with default headers)
            params: Optional query parameters

        Returns:
            Dictionary containing response data, status code, and metadata
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = {**self.default_headers, **(headers or {})}

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=merged_headers,
                    params=params,
                    timeout=self.timeout,
                )

                response.raise_for_status()

                return {
                    "data": response.json(),
                    "status_code": response.status_code,
                    "url": url,
                    "timestamp": self._current_timestamp(),
                    "success": True,
                }

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    return {
                        "data": None,
                        "status_code": (
                            e.response.status_code
                            if hasattr(e, "response") and e.response is not None
                            else None
                        ),
                        "url": url,
                        "timestamp": self._current_timestamp(),
                        "error": str(e),
                        "success": False,
                    }
                time.sleep(2**attempt)

        return {
            "data": None,
            "status_code": None,
            "url": url,
            "timestamp": self._current_timestamp(),
            "error": "Max retries exceeded",
            "success": False,
        }

    def fetch_paginated(
        self,
        endpoint: str,
        page_param: str = "page",
        per_page_param: str = "per_page",
        per_page: int = 100,
        max_pages: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Fetch paginated data from API endpoint.

        Args:
            endpoint: API endpoint path
            page_param: Query parameter name for page number
            per_page_param: Query parameter name for items per page
            per_page: Number of items per page
            max_pages: Maximum number of pages to fetch (None for all)
            headers: Optional HTTP headers

        Returns:
            Dictionary containing all paginated data, status code, and metadata
        """
        all_data = []
        page = 1
        has_more = True

        while has_more and (max_pages is None or page <= max_pages):
            params = {page_param: page, per_page_param: per_page}
            response = self.fetch(endpoint, headers=headers, params=params)

            if not response["success"]:
                return response

            page_data = response["data"]
            if isinstance(page_data, list):
                if len(page_data) == 0:
                    has_more = False
                else:
                    all_data.extend(page_data)
                    page += 1
            else:
                has_more = False

        return {
            "data": all_data,
            "status_code": response["status_code"],
            "url": response["url"],
            "timestamp": response["timestamp"],
            "success": True,
            "total_records": len(all_data),
        }

    @staticmethod
    def _current_timestamp() -> str:
        """Return an ISO formatted UTC timestamp."""
        return datetime.now(UTC).isoformat()
