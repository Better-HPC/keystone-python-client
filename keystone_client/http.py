"""Lower level HTTP client interface with automatic header/cookie handling.

The `http` module provides a consistent HTTP client interface for users
needing to perform synchronous and asynchronous HTTP requests against the
Keystone API. It offers streamlined support for common HTTP methods with
automatic URL normalization, session management, and CSRF token handling.
"""

from __future__ import annotations

import abc
import re
import uuid
from typing import Literal
from urllib.parse import urljoin, urlparse

import httpx
from httpx import AsyncBaseTransport, AsyncClient, BaseTransport, Client

__all__ = ['AsyncHTTPClient', 'HTTPClient']

DEFAULT_TIMEOUT = 15
HTTP_METHOD = Literal["get", "post", "put", "patch", "delete"]


class HTTPBase:
    """Base class with shared HTTP constants and helpers."""

    _CSRF_COOKIE = "csrftoken"
    _CSRF_HEADER = "X-CSRFToken"
    _CID_HEADER = "X-KEYSTONE-CID"

    # HTTP client to be implemented by subclasses
    _client: Client | AsyncClient

    def __init__(self, base_url: str) -> None:
        """Normalize the API url and initialize a session-specific client ID."""

        self._cid = str(uuid.uuid4())
        self._base_url = self.normalize_url(base_url)

    @property
    def base_url(self) -> str:
        """Return the normalized server URL."""

        return self._base_url

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize a URL with an enforced trailing slash.

        Args:
            url: The URL to normalize.

        Returns:
            A normalized URL with a trailing slash.
        """

        parts = urlparse(url)
        path = re.sub(r"/{2,}", "/", parts.path).rstrip("/") + "/"
        return parts._replace(path=path).geturl()

    def get_application_headers(self) -> dict[str, str]:
        """Return application specific headers for the current session"""

        headers = {self._CID_HEADER: self._cid}
        if csrf_token := self._client.cookies.get(self._CSRF_COOKIE):
            headers[self._CSRF_HEADER] = csrf_token

        return headers


class ClientInterface(abc.ABC):
    """Abstract class used to enforce a common interface across HTTP client classes."""

    @abc.abstractmethod
    def send_request(self, method: HTTP_METHOD, endpoint: str, **kwargs) -> httpx.Response:
        """Send an HTTP request."""

    @abc.abstractmethod
    def http_get(
        self,
        endpoint: str,
        params: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> httpx.Response:
        """Send a GET request."""

    @abc.abstractmethod
    def http_post(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        files: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> httpx.Response:
        """Send a POST request."""

    @abc.abstractmethod
    def http_put(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        files: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> httpx.Response:
        """Send a PUT request."""

    @abc.abstractmethod
    def http_patch(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        files: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> httpx.Response:
        """Send a PATCH request."""

    @abc.abstractmethod
    def http_delete(
        self,
        endpoint: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> httpx.Response:
        """Send a DELETE request."""


class HTTPClient(ClientInterface, HTTPBase):
    """Synchronous HTTP Client."""

    def __init__(self, base_url: str, transport: BaseTransport | None = None) -> None:
        """Initialize a new HTTP session.

        Args:
            base_url: The API base URL.
            transport: Optional HTTPX transport layer to use for HTTP requests.
        """

        super().__init__(base_url)
        self._client = Client(base_url=self._base_url, transport=transport)

    def send_request(self, method: HTTP_METHOD, endpoint: str, **kwargs) -> httpx.Response:
        """Send an HTTP request.

        Args:
            method: The HTTP method to use.
            endpoint: API endpoint relative to the base URL.
            **kwargs: Any additional arguments accepted by `httpx.Client.request`.

        Returns:
            The HTTP response.
        """

        url = self.normalize_url(urljoin(self.base_url, endpoint))
        headers = self.get_application_headers()
        return self._client.request(method=method, url=url, headers=headers, **kwargs)

    def http_get(
        self,
        endpoint: str,
        params: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send a GET request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            params: Query parameters to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP Response.
        """

        return self.send_request("get", endpoint, params=params, timeout=timeout)

    def http_post(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        files: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send a POST request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            data: JSON data or form data to include in the POST request.
            files: Files to include in the request (for multipart/form-data).
            timeout: Seconds before the request times out.

        Returns:
            The HTTP Response.
        """

        return self.send_request("post", endpoint, data=data, files=files, timeout=timeout)

    def http_patch(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        files: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send a PATCH request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            data: JSON data or form data to include in the PATCH request.
            files: Files to include in the request (for multipart/form-data).
            timeout: Seconds before the request times out.

        Returns:
            The HTTP Response.
        """

        return self.send_request("patch", endpoint, data=data, files=files, timeout=timeout)

    def http_put(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        files: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send a PUT request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            data: JSON data or form data to include in the PUT request.
            files: Files to include in the request (for multipart/form-data).
            timeout: Seconds before the request times out.

        Returns:
            The HTTP Response.
        """

        return self.send_request("put", endpoint, data=data, files=files, timeout=timeout)

    def http_delete(self, endpoint: str, timeout: int = DEFAULT_TIMEOUT) -> httpx.Response:
        """Send a DELETE request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP response.
        """

        return self.send_request("delete", endpoint, timeout=timeout)


class AsyncHTTPClient(ClientInterface, HTTPBase):
    """Asynchronous HTTP Client."""

    def __init__(self, base_url: str, transport: AsyncBaseTransport | None = None) -> None:
        """Initialize a new asynchronous HTTP session.

        Args:
            base_url: The API base URL.
            transport: Optional HTTPX transport layer to use for HTTP requests.
        """

        super().__init__(base_url)
        self._client = AsyncClient(base_url=self._base_url, transport=transport)

    async def send_request(self, method: HTTP_METHOD, endpoint: str, **kwargs) -> httpx.Response:
        """Send an asynchronous HTTP request.

        Args:
            method: The HTTP method to use.
            endpoint: API endpoint relative to the base URL.
            **kwargs: Any additional arguments accepted by `httpx.AsyncClient.request`.

        Returns:
            The awaitable HTTP response.
        """

        url = self.normalize_url(urljoin(self.base_url, endpoint))
        headers = self.get_application_headers()
        return await self._client.request(method=method, url=url, headers=headers, **kwargs)

    async def http_get(
        self,
        endpoint: str,
        params: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send an asynchronous GET request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            params: Query parameters to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP Response.
        """

        return await self.send_request("get", endpoint, params=params, timeout=timeout)

    async def http_post(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        files: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send an asynchronous POST request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            data: JSON data or form data to include in the POST request.
            files: Files to include in the request (for multipart/form-data).
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP Response.
        """

        return await self.send_request("post", endpoint, data=data, files=files, timeout=timeout)

    async def http_patch(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        files: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send an asynchronous PATCH request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            data: JSON data or form data to include in the PATCH request.
            files: Files to include in the request (for multipart/form-data).
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP Response.
        """

        return await self.send_request("patch", endpoint, data=data, files=files, timeout=timeout)

    async def http_put(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        files: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> httpx.Response:
        """Send an asynchronous PUT request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            data: JSON data or form data to include in the PUT request.
            files: Files to include in the request (for multipart/form-data).
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP Response.
        """

        return await self.send_request("put", endpoint, data=data, files=files, timeout=timeout)

    async def http_delete(self, endpoint: str, timeout: int = DEFAULT_TIMEOUT) -> httpx.Response:
        """Send an asynchronous DELETE request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP response.
        """

        return await self.send_request("delete", endpoint, timeout=timeout)
