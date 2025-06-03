"""Keystone API Client

This module provides a client class `KeystoneAPIClient` for interacting with the
Keystone API. It streamlines communication with the API, providing methods for
authentication, data retrieval, and data manipulation.
"""

from __future__ import annotations

from functools import cached_property
from typing import Union

import httpx

from keystone_client.schema import ApiSchema
from keystone_client.http import DEFAULT_TIMEOUT, HTTPClient


class KeystoneClient(HTTPClient):
    """Client class for submitting requests to the Keystone API."""

    schema = ApiSchema()

    @cached_property
    def api_version(self) -> str:
        """Return the version number of the API server."""

        response = self.http_get("version")
        return response.text

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
        response = self._client.post(login_url, json={'username': username, 'password': password}, timeout=timeout)

        try:
            response.raise_for_status()

        except httpx.HTTPError:
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

        response = self.http_get('authentication/whoami/', timeout=timeout)
        if response.status_code == 401:
            return False

        response.raise_for_status()
        return response.status_code == 200

    def __new__(cls, *args, **kwargs) -> KeystoneClient:
        """Dynamically create CRUD methods for each data endpoint in the API schema."""

        new: KeystoneClient = super().__new__(cls)
        for endpoint in cls.schema.endpoints:
            if endpoint.method == "GET":
                method = new._retrieve_factory(endpoint.path)

            elif endpoint.method == "POST":
                method = new._create_factory(endpoint.path)

            elif endpoint.method == "PATCH":
                method = new._update_factory(endpoint.path)

            elif endpoint.method == "DELETE":
                method = new._delete_factory(endpoint.path)

            else:
                continue

            setattr(new, endpoint.operation_id, method)

        return new

    def _create_factory(self, endpoint: str) -> callable:
        """Factory function for data creation methods."""

        def create_record(**data) -> None:
            """Create an API record.

            Args:
                **data: New record values.

            Returns:
                A copy of the updated record.
            """

            response = self.http_post(endpoint, data=data)
            response.raise_for_status()
            return response.json()

        return create_record

    def _retrieve_factory(self, endpoint: str) -> callable:
        """Factory function for data retrieval methods."""

        def retrieve_record(
            pk: int | None = None,
            filters: dict | None = None,
            search: str | None = None,
            order: str | None = None,
            timeout=DEFAULT_TIMEOUT
        ) -> Union[None, dict, list[dict]]:
            """Retrieve one or more API records.

            A single record is returned when specifying a primary key, otherwise the returned
            object is a list of records. In either case, the return value is `None` when no data
            is available for the query.

            Args:
                pk: Optional primary key to fetch a specific record.
                filters: Optional query parameters to include in the request.
                search: Optionally search records for the given string.
                order: Optional order returned values by the given parameter.
                timeout: Seconds before the request times out.

            Returns:
                The data record(s) or None.
            """

            for param_name, value in zip(('_search', '_order'), (search, order)):
                if value is not None:
                    filters = filters or {}
                    filters[param_name] = value

            response = self.http_get(endpoint.format(id=pk), params=filters, timeout=timeout)

            try:
                response.raise_for_status()
                return response.json()

            except httpx.HTTPError:
                if response.status_code == 404:
                    return None

                raise

        return retrieve_record

    def _update_factory(self, endpoint: str) -> callable:
        """Factory function for data update methods."""

        def update_record(pk: int, data) -> dict:
            """Update an API record.

            Args:
                pk: Primary key of the record to update.
                data: New record values.

            Returns:
                A copy of the updated record.
            """

            response = self.http_patch(endpoint.format(id=pk), data=data)
            response.raise_for_status()
            return response.json()

        return update_record

    def _delete_factory(self, endpoint: str) -> callable:
        """Factory function for data deletion methods."""

        def delete_record(pk: int, raise_not_exists: bool = False) -> None:
            """Delete an API record.

            Args:
                pk: Primary key of the record to delete.
                raise_not_exists: Raise an error if the record does not exist.
            """

            response = self.http_delete(endpoint.format(id=pk))

            try:
                response.raise_for_status()

            except httpx.HTTPError:
                if response.status_code == 404 and not raise_not_exists:
                    return

                raise

        return delete_record
