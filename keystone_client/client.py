"""Keystone API client classes.

The `client` module provides client classes for interacting with the Keystone
API. It streamlines communication with the API, providing methods for
authentication, data retrieval, and data manipulation.
"""

import abc

import httpx
from httpx import HTTPStatusError

from keystone_client.http import AsyncHTTPClient, HTTPClient


class ClientBase(abc.ABC):
    """Base client class with shared application constants and helpers."""

    LOGIN_ENDPOINT = 'authentication/login'
    LOGOUT_ENDPOINT = 'authentication/logout'
    IDENTITY_ENDPOINT = 'authentication/whoami'

    @abc.abstractmethod
    def login(self, username: str, password: str, timeout: int) -> None:
        """Authenticate a user session."""

    @abc.abstractmethod
    def logout(self) -> None:
        """Terminate the current user session."""

    @abc.abstractmethod
    def whoami(self) -> dict:
        """Return metadata for the currently authenticated user."""

    @staticmethod
    def _handle_identity_response(response: httpx.Response) -> dict:
        """Handle identity check responses, returning empty dict on 401.

        Args:
            response: The HTTP response object.

        Returns:
            The response JSON on success or an empty dictionary if the request returned HTTP 401.
        """

        if response.status_code == 401:
            return dict()

        response.raise_for_status()
        return response.json()


class KeystoneClient(ClientBase, HTTPClient):
    """Client class for submitting synchronous requests to the Keystone API."""

    def login(self, username: str, password: str, timeout: int = httpx.USE_CLIENT_DEFAULT) -> None:
        """Authenticate a new user session.

        Args:
            username: The authentication username.
            password: The authentication password.
            timeout: Seconds before the request times out.

        Raises:
            HTTPError: If the login request fails.
        """

        self.http_post(
            endpoint=self.LOGIN_ENDPOINT,
            json={'username': username, 'password': password},
            timeout=timeout
        ).raise_for_status()

    def logout(self, timeout: int = httpx.USE_CLIENT_DEFAULT) -> None:
        """Log out the current user session.

        Args:
            timeout: Seconds before the request times out.
        """

        response = self.http_post(
            endpoint=self.LOGOUT_ENDPOINT,
            timeout=timeout
        )

        try:
            response.raise_for_status()

        except HTTPStatusError as exception:
            if exception.response.status_code != 401:
                raise

    def whoami(self, timeout: int = httpx.USE_CLIENT_DEFAULT) -> dict:
        """Return metadata for the currently authenticated user.

        Returns an empty dictionary if the current session is not authenticated.

        Args:
            timeout: Seconds before the request times out.
        """

        response = self.http_get(self.IDENTITY_ENDPOINT, timeout=timeout)
        return self._handle_identity_response(response)


class AsyncKeystoneClient(ClientBase, AsyncHTTPClient):
    """Client class for submitting asynchronous requests to the Keystone API."""

    async def login(self, username: str, password: str, timeout: int = httpx.USE_CLIENT_DEFAULT) -> None:
        """Authenticate a new user session.

        Args:
            username: The authentication username.
            password: The authentication password.
            timeout: Seconds before the request times out.

        Raises:
            HTTPError: If the login request fails.
        """

        response = await self.http_post(
            endpoint=self.LOGIN_ENDPOINT,
            json={'username': username, 'password': password},
            timeout=timeout
        )

        response.raise_for_status()

    async def logout(self, timeout: int = httpx.USE_CLIENT_DEFAULT) -> None:
        """Log out the current user session.

        Args:
            timeout: Seconds before the request times out.
        """

        response = await self.http_post(
            endpoint=self.LOGOUT_ENDPOINT,
            timeout=timeout
        )

        try:
            response.raise_for_status()

        except HTTPStatusError as exception:
            if exception.response.status_code != 401:
                raise

    async def whoami(self, timeout: int = httpx.USE_CLIENT_DEFAULT) -> dict:
        """Return metadata for the currently authenticated user.

        Returns an empty dictionary if the current session is not authenticated.

        Args:
            timeout: Seconds before the request times out.
        """

        response = await self.http_get(self.IDENTITY_ENDPOINT, timeout=timeout)
        return self._handle_identity_response(response)
