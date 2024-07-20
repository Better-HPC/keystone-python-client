from __future__ import annotations

import urllib.parse
from typing import Literal

import requests

from keystone_client.authentication import AuthenticationManager
from keystone_client.schema import Schema

HTTPMethod = Literal["get", "post", "put", "patch", "delete"]


class HTTPClient:
    """Low level API client for sending standard HTTP operations"""

    schema = Schema()
    default_timeout = 15

    def __init__(self, url: str) -> None:
        """Initialize the class

        Args:
            url: The base URL for a running Keystone API server
        """

        self._url = url.rstrip('/') + '/'
        self._auth = AuthenticationManager(
            self.resolve_endpoint(self.schema.auth.new),
            self.resolve_endpoint(self.schema.auth.refresh),
            self.resolve_endpoint(self.schema.auth.blacklist)
        )
        self._api_version: str | None = None

    @property
    def url(self) -> str:
        """Return the server URL"""

        return self._url

    def resolve_endpoint(self, endpoint: str) -> str:
        """Resolve a partial endpoint into a fully qualified URL

        Args:
            endpoint: The API endpoint

        Returns:
            The fully qualified endpoint URL
        """

        return urllib.parse.urljoin(self.url, endpoint.strip('/')) + '/'

    def _send_request(self, method: HTTPMethod, endpoint: str, **kwargs) -> requests.Response:
        """Send an HTTP request

        Args:
            method: The HTTP method to use
            endpoint: The complete url to send the request to
            timeout: Seconds before the request times out

        Returns:
            An HTTP response
        """

        url = self._resolve_endpoint(endpoint)
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def http_get(
        self,
        endpoint: str,
        params: dict[str, any] | None = None,
        timeout: int = default_timeout
    ) -> requests.Response:
        """Send a GET request to an API endpoint

        Args:
            endpoint: API endpoint to send the request to
            params: Query parameters to include in the request
            timeout: Seconds before the request times out

        Returns:
            The response from the API in the specified format

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        return self._send_request("get", endpoint, params=params, timeout=timeout)

    def http_post(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = default_timeout
    ) -> requests.Response:
        """Send a POST request to an API endpoint

        Args:
            endpoint: API endpoint to send the request to
            data: JSON data to include in the POST request
            timeout: Seconds before the request times out

        Returns:
            The response from the API in the specified format

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        return self._send_request("post", endpoint, data=data, timeout=timeout)

    def http_patch(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = default_timeout
    ) -> requests.Response:
        """Send a PATCH request to an API endpoint

        Args:
            endpoint: API endpoint to send the request to
            data: JSON data to include in the PATCH request
            timeout: Seconds before the request times out

        Returns:
            The response from the API in the specified format

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        return self._send_request("patch", endpoint, data=data, timeout=timeout)

    def http_put(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = default_timeout
    ) -> requests.Response:
        """Send a PUT request to an endpoint

        Args:
            endpoint: API endpoint to send the request to
            data: JSON data to include in the PUT request
            timeout: Seconds before the request times out

        Returns:
            The API response

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        return self._send_request("put", endpoint, data=data, timeout=timeout)

    def http_delete(
        self,
        endpoint: str,
        timeout: int = default_timeout
    ) -> requests.Response:
        """Send a DELETE request to an endpoint

        Args:
            endpoint: API endpoint to send the request to
            timeout: Seconds before the request times out

        Returns:
            The API response

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        return self._send_request("delete", endpoint, timeout=timeout)
