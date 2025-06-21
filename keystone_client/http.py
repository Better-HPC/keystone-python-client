"""Lower level HTTP client interface with automatic header/cookie handling.

The `http` module provides a consistent HTTP client interface for users
needing to perform synchronous and asynchronous HTTP requests against the
Keystone API. It offers streamlined support for common HTTP methods with
automatic URL normalization, session management, and CSRF token handling.
"""

import re
import uuid
from urllib.parse import urljoin, urlparse

import httpx

from .types import *

__all__ = ['AsyncHTTPClient', 'HTTPClient']

DEFAULT_TIMEOUT = 15


class HTTPBase:
    """Base class with shared HTTP constants and helpers."""

    CSRF_COOKIE = "csrftoken"
    CSRF_HEADER = "X-CSRFToken"
    CID_HEADER = "X-KEYSTONE-CID"

    # HTTP client to be implemented by subclasses
    _client: httpx.Client | httpx.AsyncClient

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

    def get_application_headers(self, overrides: dict | None = None) -> dict[str, str]:
        """Return application specific headers for the current session"""

        headers = {self.CID_HEADER: self._cid}
        if csrf_token := self._client.cookies.get(self.CSRF_COOKIE):
            headers[self.CSRF_HEADER] = csrf_token

        if overrides is not None:
            headers.update(overrides)

        return headers


class HTTPClient(HTTPBase):
    """Synchronous HTTP Client."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: int | None = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None
    ) -> None:
        """Initialize a new HTTP session.

        Args:
            base_url: The API base URL.
            transport: Optional HTTPX transport layer to use for HTTP requests.
        """

        super().__init__(base_url)
        self._client = httpx.Client(base_url=self._base_url, timeout=timeout, transport=transport)

    def send_request(
        self,
        method: HttpMethod,
        endpoint: str,
        *,
        headers: dict = None,
        content: RequestContent | None = None,
        json: RequestContent | None = None,
        files: RequestFiles | None = None,
        params: QueryParamTypes | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an HTTP request.

        Args:
            method: The HTTP method to use.
            endpoint: API endpoint relative to the base URL.
            headers: Extend application headers with custom values.
            content: Optional raw content to include in the request body.
            json: Optional JSON data to include in the request body.
            files: Optional file data to include in the request.
            params: Optional query parameters to include in the request URL.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP response.
        """

        url = self.normalize_url(urljoin(self.base_url, endpoint))
        application_headers = self.get_application_headers(headers)
        return self._client.request(
            method=method,
            url=url,
            headers=application_headers,
            content=content,
            json=json,
            files=files,
            params=params,
            timeout=timeout,
        )

    def http_get(
        self,
        endpoint: str,
        params: QueryParamTypes | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a GET request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            params: Query parameters to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP Response.
        """

        return self.send_request("get", endpoint, params=params, timeout=timeout)  # pragma: no cover

    def http_post(
        self,
        endpoint: str,
        json: RequestData | None = None,
        files: RequestFiles | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a POST request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: Files data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP Response.
        """

        return self.send_request("post", endpoint, json=json, files=files, timeout=timeout)  # pragma: no cover

    def http_patch(
        self,
        endpoint: str,
        json: RequestData | None = None,
        files: RequestFiles | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a PATCH request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: Files data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP Response.
        """

        return self.send_request("patch", endpoint, json=json, files=files, timeout=timeout)  # pragma: no cover

    def http_put(
        self,
        endpoint: str,
        json: RequestData | None = None,
        files: RequestFiles | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a PUT request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: Files data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP Response.
        """

        return self.send_request("put", endpoint, json=json, files=files, timeout=timeout)  # pragma: no cover

    def http_delete(self, endpoint: str, timeout: int = httpx.USE_CLIENT_DEFAULT) -> httpx.Response:
        """Send a DELETE request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP response.
        """

        return self.send_request("delete", endpoint, timeout=timeout)  # pragma: no cover


class AsyncHTTPClient(HTTPBase):
    """Asynchronous HTTP Client."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: int | None = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None
    ) -> None:
        """Initialize a new HTTP session.

        Args:
            base_url: The API base URL.
            transport: Optional HTTPX transport layer to use for HTTP requests.
        """

        super().__init__(base_url)
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=timeout, transport=transport)

    async def send_request(
        self,
        method: HttpMethod,
        endpoint: str,
        *,
        headers: dict = None,
        content: RequestContent | None = None,
        json: dict | None = None,
        files: RequestFiles | None = None,
        params: QueryParamTypes | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an HTTP request.

        Args:
            method: The HTTP method to use.
            endpoint: API endpoint relative to the base URL.
            headers: Extend application headers with custom values.
            content: Optional raw content to include in the request body.
            json: Optional JSON data to include in the request body.
            files: Optional file data to include in the request.
            params: Optional query parameters to include in the request URL.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP response.
        """

        url = self.normalize_url(urljoin(self.base_url, endpoint))
        application_headers = self.get_application_headers(headers)
        return await self._client.request(
            method=method,
            url=url,
            headers=application_headers,
            content=content,
            json=json,
            files=files,
            params=params,
            timeout=timeout
        )

    async def http_get(
        self,
        endpoint: str,
        params: QueryParamTypes | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an asynchronous GET request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            params: Query parameters to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP Response.
        """

        return await self.send_request("get", endpoint, params=params, timeout=timeout)  # pragma: no cover

    async def http_post(
        self,
        endpoint: str,
        json: RequestData | None = None,
        files: RequestFiles | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an asynchronous POST request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: Files data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP Response.
        """

        return await self.send_request("post", endpoint, json=json, files=files, timeout=timeout)  # pragma: no cover

    async def http_patch(
        self,
        endpoint: str,
        json: RequestData | None = None,
        files: RequestFiles | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an asynchronous PATCH request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: Files data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP Response.
        """

        return await self.send_request("patch", endpoint, json=json, files=files, timeout=timeout)  # pragma: no cover

    async def http_put(
        self,
        endpoint: str,
        json: RequestData | None = None,
        files: RequestFiles | None = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an asynchronous PUT request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: Files data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP Response.
        """

        return await self.send_request("put", endpoint, json=json, files=files, timeout=timeout)  # pragma: no cover

    async def http_delete(self, endpoint: str, timeout: int = DEFAULT_TIMEOUT) -> httpx.Response:
        """Send an asynchronous DELETE request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP response.
        """

        return await self.send_request("delete", endpoint, timeout=timeout)  # pragma: no cover
