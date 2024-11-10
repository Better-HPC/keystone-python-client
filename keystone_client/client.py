"""Keystone API Client

This module provides a client class `KeystoneAPIClient` for interacting with the
Keystone API. It streamlines communication with the API, providing methods for
authentication, data retrieval, and data manipulation.
"""

from __future__ import annotations

from functools import cached_property
from typing import Literal, Union
from urllib.parse import urljoin

import requests
from requests import HTTPError, Session

from keystone_client.schema import Endpoint, Schema

DEFAULT_TIMEOUT = 15


class HTTPClient:
    """Low level API client for sending standard HTTP operations."""

    schema = Schema()

    def __init__(self, url: str) -> None:
        """Initialize the class.

        Args:
            url: The base URL for a Keystone API server.
        """

        self._url = url.rstrip('/') + '/'
        self._session = Session()

    @property
    def url(self) -> str:
        """Return the server URL."""

        return self._url

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
        url = urljoin(self.url, endpoint)

        response = self._session.request(method=method, url=url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

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


class KeystoneClient(HTTPClient):
    """Client class for submitting requests to the Keystone API."""

    @cached_property
    def api_version(self) -> str:
        """Return the version number of the API server."""

        response = self.http_get("version")
        response.raise_for_status()
        return response.text

    def __new__(cls, *args, **kwargs) -> KeystoneClient:
        """Dynamically create CRUD methods for each data endpoint in the API schema."""

        new: KeystoneClient = super().__new__(cls)

        new.create_allocation = new._create_factory(cls.schema.allocations)
        new.retrieve_allocation = new._retrieve_factory(cls.schema.allocations)
        new.update_allocation = new._update_factory(cls.schema.allocations)
        new.delete_allocation = new._delete_factory(cls.schema.allocations)

        new.create_cluster = new._create_factory(cls.schema.clusters)
        new.retrieve_cluster = new._retrieve_factory(cls.schema.clusters)
        new.update_cluster = new._update_factory(cls.schema.clusters)
        new.delete_cluster = new._delete_factory(cls.schema.clusters)

        new.create_request = new._create_factory(cls.schema.requests)
        new.retrieve_request = new._retrieve_factory(cls.schema.requests)
        new.update_request = new._update_factory(cls.schema.requests)
        new.delete_request = new._delete_factory(cls.schema.requests)

        new.create_team = new._create_factory(cls.schema.teams)
        new.retrieve_team = new._retrieve_factory(cls.schema.teams)
        new.update_team = new._update_factory(cls.schema.teams)
        new.delete_team = new._delete_factory(cls.schema.teams)

        new.create_membership = new._create_factory(cls.schema.memberships)
        new.retrieve_membership = new._retrieve_factory(cls.schema.memberships)
        new.update_membership = new._update_factory(cls.schema.memberships)
        new.delete_membership = new._delete_factory(cls.schema.memberships)

        new.create_user = new._create_factory(cls.schema.users)
        new.retrieve_user = new._retrieve_factory(cls.schema.users)
        new.update_user = new._update_factory(cls.schema.users)
        new.delete_user = new._delete_factory(cls.schema.users)

        return new

    def _create_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data creation methods."""

        def create_record(**data) -> None:
            """Create an API record.

            Args:
                **data: New record values.

            Returns:
                A copy of the updated record.
            """

            url = endpoint.join_url(self.url)
            response = self.http_post(url, data=data)
            response.raise_for_status()
            return response.json()

        return create_record

    def _retrieve_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data retrieval methods."""

        def retrieve_record(
            pk: int | None = None,
            filters: dict | None = None,
            timeout=DEFAULT_TIMEOUT
        ) -> Union[None, dict, list[dict]]:
            """Retrieve one or more API records.

            A single record is returned when specifying a primary key, otherwise the returned
            object is a list of records. In either case, the return value is `None` when no data
            is available for the query.

            Args:
                pk: Optional primary key to fetch a specific record.
                filters: Optional query parameters to include in the request.
                timeout: Seconds before the request times out.

            Returns:
                The data record(s) or None.
            """

            url = endpoint.join_url(self.url, pk)

            try:
                response = self.http_get(url, params=filters, timeout=timeout)
                response.raise_for_status()
                return response.json()

            except requests.HTTPError as exception:
                if exception.response.status_code == 404:
                    return None

                raise

        return retrieve_record

    def _update_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data update methods."""

        def update_record(pk: int, data) -> dict:
            """Update an API record.

            Args:
                pk: Primary key of the record to update.
                data: New record values.

            Returns:
                A copy of the updated record.
            """

            url = endpoint.join_url(self.url, pk)
            response = self.http_patch(url, data=data)
            response.raise_for_status()
            return response.json()

        return update_record

    def _delete_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data deletion methods."""

        def delete_record(pk: int, raise_not_exists: bool = False) -> None:
            """Delete an API record.

            Args:
                pk: Primary key of the record to delete.
                raise_not_exists: Raise an error if the record does not exist.
            """

            url = endpoint.join_url(self.url, pk)

            try:
                response = self.http_delete(url)
                response.raise_for_status()

            except requests.HTTPError as exception:
                if exception.response.status_code == 404 and not raise_not_exists:
                    return

                raise

        return delete_record
