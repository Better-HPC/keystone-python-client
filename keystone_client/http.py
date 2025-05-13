from __future__ import annotations

import uuid
from typing import Literal
from urllib.parse import urljoin, urlparse

import requests
from requests import HTTPError, Session

from keystone_client.schema import Schema

DEFAULT_TIMEOUT = 15


class HTTPClient:
    """Low level API client for sending standard HTTP operations."""

    schema = Schema()

    def __init__(self, url: str) -> None:
        """Initialize the class.

        Args:
            url: The base URL for a Keystone API server.
        """

        self._url = self._normalize_url(url)
        self._session = Session()
        self._session.headers['X-KEYSTONE-CID'] = str(uuid.uuid4())

    @property
    def url(self) -> str:
        """Return the server URL."""

        return self._url

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

    def _csrf_headers(self) -> dict:
        """Return the CSRF headers for the current session"""

        headers = dict()
        if csrf_token := self._session.cookies.get('csrftoken'):
            headers['X-CSRFToken'] = csrf_token

        return headers

    def _send_request(
        self,
        method: Literal["get", "post", "put", "patch", "delete"],
        endpoint: str,
        **kwargs
    ) -> requests.Response:
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

        headers = self._csrf_headers()
        url = self._normalize_url(urljoin(self.url, endpoint))

        response = self._session.request(method=method, url=url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    def login(self, username: str, password: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Authenticate a new user session.

        Args:
            username: The authentication username.
            password: The authentication password.
            timeout: Seconds before the request times out.

        Raises:
            requests.HTTPError: If the login request fails.
        """

        # Prevent HTTP errors raised when authenticating an existing session
        login_url = self.schema.login.join_url(self.url)
        response = self._session.post(login_url, json={'username': username, 'password': password}, timeout=timeout)

        try:
            response.raise_for_status()

        except HTTPError:
            if not self.is_authenticated(timeout=timeout):
                raise

    def logout(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Logout the current user session.

        Args:
            timeout: Seconds before the blacklist request times out.
        """

        logout_url = self.schema.logout.join_url(self.url)
        response = self.http_post(logout_url, timeout=timeout)
        response.raise_for_status()

    def is_authenticated(self, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Query the server for the current session's authentication status.

        Args:
            timeout: Seconds before the blacklist request times out.
        """

        response = self._session.get(f'{self.url}/authentication/whoami/', timeout=timeout)
        if response.status_code == 401:
            return False

        response.raise_for_status()
        return response.status_code == 200

    def http_get(
        self,
        endpoint: str,
        params: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> requests.Response:
        """Send a GET request to an API endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            params: Query parameters to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The response from the API in the specified format.

        Raises:
            requests.HTTPError: If the request returns an error code.
        """

        return self._send_request("get", endpoint, params=params, timeout=timeout)

    def http_post(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> requests.Response:
        """Send a POST request to an API endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            data: JSON data to include in the POST request.
            timeout: Seconds before the request times out.

        Returns:
            The response from the API in the specified format.

        Raises:
            requests.HTTPError: If the request returns an error code.
        """

        return self._send_request("post", endpoint, data=data, timeout=timeout)

    def http_patch(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> requests.Response:
        """Send a PATCH request to an API endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            data: JSON data to include in the PATCH request.
            timeout: Seconds before the request times out.

        Returns:
            The response from the API in the specified format.

        Raises:
            requests.HTTPError: If the request returns an error code.
        """

        return self._send_request("patch", endpoint, data=data, timeout=timeout)

    def http_put(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> requests.Response:
        """Send a PUT request to an endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            data: JSON data to include in the PUT request.
            timeout: Seconds before the request times out.

        Returns:
            The API response.

        Raises:
            requests.HTTPError: If the request returns an error code.
        """

        return self._send_request("put", endpoint, data=data, timeout=timeout)

    def http_delete(
        self,
        endpoint: str,
        timeout: int = DEFAULT_TIMEOUT
    ) -> requests.Response:
        """Send a DELETE request to an endpoint.

        Args:
            endpoint: API endpoint to send the request to.
            timeout: Seconds before the request times out.

        Returns:
            The API response.

        Raises:
            requests.HTTPError: If the request returns an error code.
        """

        return self._send_request("delete", endpoint, timeout=timeout)
