"""Keystone API Client

This module provides a client class `KeystoneAPIClient` for interacting with the
Keystone API. It streamlines communication with the API, providing methods for
authentication, data retrieval, and data manipulation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx

from keystone_client.http import DEFAULT_TIMEOUT, HTTPClient
from keystone_client.schema import Endpoint, Schema

__all__ = ['KeystoneClient']


class KeystoneClient(HTTPClient):
    """Client class for submitting requests to the Keystone API."""

    schema = Schema()

    LOGIN_ENDPOINT = Endpoint('authentication/login')
    LOGOUT_ENDPOINT = Endpoint('authentication/logout')
    IDENTITY_ENDPOINT = Endpoint('authentication/whoami')

    def login(self, username: str, password: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Authenticate a new user session.

        Args:
            username: The authentication username.
            password: The authentication password.
            timeout: Seconds before the request times out.

        Raises:
            requests.HTTPError: If the login request fails.
        """

        login_url = self.normalize_url(urljoin(self.base_url, self.LOGIN_ENDPOINT))
        credentials = {'username': username, 'password': password}

        response = self.http_post(login_url, json=credentials, timeout=timeout)
        response.raise_for_status()

    def logout(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Logout the current user session.

        Args:
            timeout: Seconds before the request times out.
        """

        logout_url = self.normalize_url(urljoin(self.base_url, self.LOGOUT_ENDPOINT))
        response = self.http_post(logout_url, timeout=timeout)
        response.raise_for_status()

    def is_authenticated(self, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """Return metadata for the currently authenticated user.

        Returns an empty dictionary if the current session is not authenticated.

        Args:
            timeout: Seconds before the request times out.
        """

        identity_url = self.normalize_url(urljoin(self.base_url, self.IDENTITY_ENDPOINT))
        response = self.http_get(identity_url, timeout=timeout)

        if response.status_code == 401:
            return {}

        response.raise_for_status()
        return response.json()

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

            url = endpoint.join_url(self.base_url)
            response = self.http_post(url, json=data)
            response.raise_for_status()
            return response.json()

        return create_record

    def _retrieve_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data retrieval methods."""

        def retrieve_record(
            pk: Optional[int] = None,
            filters: Optional[Dict[str, Any]] = None,
            search: Optional[str] = None,
            order: Optional[str] = None,
            timeout: int = DEFAULT_TIMEOUT
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

            url = endpoint.join_url(self.base_url, pk)

            for param_name, value in zip(('_search', '_order'), (search, order)):
                if value is not None:
                    filters = filters or {}
                    filters[param_name] = value

            response = self.http_get(url, params=filters, timeout=timeout)

            try:
                response.raise_for_status()
                return response.json()

            except httpx.HTTPError:
                if response.status_code == 404:
                    return None

                raise

        return retrieve_record

    def _update_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data update methods."""

        def update_record(pk: int, data: dict) -> dict:
            """Update an API record.

            Args:
                pk: Primary key of the record to update.
                data: New record values.

            Returns:
                A copy of the updated record.
            """

            url = endpoint.join_url(self.base_url, pk)
            response = self.http_patch(url, json=data)
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

            url = endpoint.join_url(self.base_url, pk)
            response = self.http_delete(url)

            try:
                response.raise_for_status()

            except httpx.HTTPError:
                if response.status_code == 404 and not raise_not_exists:
                    return

                raise

        return delete_record
