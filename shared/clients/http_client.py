"""Agnostic HTTP client for all API integrations."""

from __future__ import annotations

from typing import Any, Literal

import httpx


class HttpClient:
    """Generic HTTP client for all third-party API calls.

    Used by device integrations (August, TP-Link, Hikvision, etc) to make
    vendor API requests. Handles retries, timeouts, auth, and error handling.
    """

    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        base_url: str | None = None,
    ):
        """Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Number of retries for failed requests
            base_url: Optional base URL for all requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = base_url
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        auth: tuple[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make GET request.

        Args:
            url: Request URL
            headers: Optional request headers
            params: Optional query parameters
            auth: Optional (username, password) tuple for basic auth
            **kwargs: Additional httpx request options

        Returns:
            Response JSON as dict

        Raises:
            httpx.HTTPError: On request failure
        """
        return await self._request(
            "GET",
            url,
            headers=headers,
            params=params,
            auth=auth,
            **kwargs,
        )

    async def post(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        auth: tuple[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make POST request.

        Args:
            url: Request URL
            json: JSON body
            data: Form data or string body
            headers: Optional request headers
            params: Optional query parameters
            auth: Optional (username, password) tuple for basic auth
            **kwargs: Additional httpx request options

        Returns:
            Response JSON as dict

        Raises:
            httpx.HTTPError: On request failure
        """
        return await self._request(
            "POST",
            url,
            json=json,
            data=data,
            headers=headers,
            params=params,
            auth=auth,
            **kwargs,
        )

    async def put(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        auth: tuple[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make PUT request."""
        return await self._request(
            "PUT",
            url,
            json=json,
            headers=headers,
            params=params,
            auth=auth,
            **kwargs,
        )

    async def patch(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        auth: tuple[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make PATCH request."""
        return await self._request(
            "PATCH",
            url,
            json=json,
            headers=headers,
            params=params,
            auth=auth,
            **kwargs,
        )

    async def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        auth: tuple[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make DELETE request."""
        return await self._request(
            "DELETE",
            url,
            headers=headers,
            params=params,
            auth=auth,
            **kwargs,
        )

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
        url: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Internal request handler with retries.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: httpx request options

        Returns:
            Response JSON as dict

        Raises:
            httpx.HTTPError: On repeated failures after retries
        """
        full_url = self.base_url + url if self.base_url and not url.startswith("http") else url

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, full_url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                last_error = e
                # Retry on timeout or 5xx errors
                if isinstance(e, (httpx.TimeoutException, httpx.RemoteProtocolError)):
                    if attempt < self.max_retries - 1:
                        continue

        raise last_error or httpx.RequestError(f"Failed after {self.max_retries} attempts")

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> HttpClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
