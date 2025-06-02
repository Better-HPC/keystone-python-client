from __future__ import annotations

import uuid
from typing import Literal
from urllib.parse import urlparse

import httpx
from httpx import Client

DEFAULT_TIMEOUT = 15


class HTTPClient:
    """Low level API client for sending standard HTTP operations."""

    _CID_HEADER = 'X-KEYSTONE-CID'
    _CSRF_COOKIE = 'csrftoken'
    _CSRF_HEADER = 'X-CSRFToken'

    def __init__(self, base_url: str) -> None:
        """Initialize the class.

        Args:
            base_url: The base URL for a Keystone API server.
        """

        self._cid = str(uuid.uuid4())
        self._client = Client(base_url=self._normalize_url(base_url))

    @property
    def base_url(self) -> str:
        """Return the server URL."""

        return str(self._client.base_url)

    def _normalize_url(self, url: str) -> str:
        """Return a copy of the given url with a trailing slash enforced on the URL path.

        Args:
            url: The URL to normalize.

        Returns:
            A normalized copy of the URL.
        """

        parts = urlparse(url)
        return parts._replace(
            path=parts.path.rstrip('/') + '/',
        ).geturl()

    def _get_headers(self) -> dict:
        """Return the CSRF headers for the current session"""

        headers = {self._CID_HEADER: self._cid}
        if csrf_token := self._client.cookies.get('csrftoken'):
            headers['X-CSRFToken'] = csrf_token

        return headers

    def _send_request(
        self,
        method: Literal["get", "post", "put", "patch", "delete"],
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Send an HTTP request.

        Args:
            method: The HTTP method to use.
            data: JSON data to include in the POST request.
            endpoint: The complete url to send the request to.
            params: Query parameters to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            An HTTP response.
        """

        headers = self._get_headers()
        url = self._normalize_url(endpoint)

        response = self._client.request(method=method, url=url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    def http_get(
        self,
        endpoint: str,
        params: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send a GET request to an API endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            params: Query parameters to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The response from the API in the specified format.

        Raises:
            httpx.HTTPError: If the request returns an error code.
        """

        return self._send_request("get", endpoint, params=params, timeout=timeout)

    def http_post(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send a POST request to an API endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            data: JSON data to include in the POST request.
            timeout: Seconds before the request times out.

        Returns:
            The response from the API in the specified format.

        Raises:
            httpx.HTTPError: If the request returns an error code.
        """

        return self._send_request("post", endpoint, data=data, timeout=timeout)

    def http_patch(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send a PATCH request to an API endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            data: JSON data to include in the PATCH request.
            timeout: Seconds before the request times out.

        Returns:
            The response from the API in the specified format.

        Raises:
            httpx.HTTPError: If the request returns an error code.
        """

        return self._send_request("patch", endpoint, data=data, timeout=timeout)

    def http_put(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send a PUT request to an endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            data: JSON data to include in the PUT request.
            timeout: Seconds before the request times out.

        Returns:
            The API response.

        Raises:
            httpx.HTTPError: If the request returns an error code.
        """

        return self._send_request("put", endpoint, data=data, timeout=timeout)

    def http_delete(
        self,
        endpoint: str,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send a DELETE request to an endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            timeout: Seconds before the request times out.

        Returns:
            The API response.

        Raises:
            httpx.HTTPError: If the request returns an error code.
        """

        return self._send_request("delete", endpoint, timeout=timeout)
