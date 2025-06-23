"""Keystone API client classes.

This module provides client classes for interacting with the Keystone API.
It streamlines communication with the API, providing methods for
authentication, data retrieval, and data manipulation.
"""

from __future__ import annotations

import abc
from typing import Any, Dict, Optional, Union

import httpx

from keystone_client.http import AsyncHTTPClient, DEFAULT_TIMEOUT, HTTPClient
from keystone_client.schema import Endpoint, Schema

__all__ = ['AsyncKeystoneClient', 'KeystoneClient']


class ClientBase(abc.ABC):
    """Base client class with shared application constants and helpers."""

    schema = Schema()

    LOGIN_ENDPOINT = Endpoint('authentication/login')
    LOGOUT_ENDPOINT = Endpoint('authentication/logout')
    IDENTITY_ENDPOINT = Endpoint('authentication/whoami')

    def __new__(cls, *args, **kwargs):
        """Dynamically create CRUD methods for each data endpoint in the API schema."""

        new = super().__new__(cls)
        for name, endpoint in {
            'allocation': cls.schema.allocations,
            'cluster': cls.schema.clusters,
            'request': cls.schema.requests,
            'team': cls.schema.teams,
            'membership': cls.schema.memberships,
            'user': cls.schema.users,
        }.items():
            setattr(new, f'create_{name}', new._create_factory(endpoint))
            setattr(new, f'retrieve_{name}', new._retrieve_factory(endpoint))
            setattr(new, f'update_{name}', new._update_factory(endpoint))
            setattr(new, f'delete_{name}', new._delete_factory(endpoint))

        return new

    @abc.abstractmethod
    def _create_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data creation methods."""

    @abc.abstractmethod
    def _retrieve_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data retrieval methods."""

    @abc.abstractmethod
    def _update_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data update methods."""

    @abc.abstractmethod
    def _delete_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data deletion methods."""


class KeystoneClient(ClientBase, HTTPClient):
    """Client class for submitting synchronous requests to the Keystone API."""

    def login(self, username: str, password: str, timeout: int = DEFAULT_TIMEOUT) -> None:
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

    def logout(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Logout the current user session.

        Args:
            timeout: Seconds before the request times out.
        """

        self.http_post(
            endpoint=self.LOGOUT_ENDPOINT,
            timeout=timeout
        ).raise_for_status()

    def is_authenticated(self, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """Return metadata for the currently authenticated user.

        Returns an empty dictionary if the current session is not authenticated.

        Args:
            timeout: Seconds before the request times out.
        """

        response = self.http_get(self.IDENTITY_ENDPOINT, timeout=timeout)
        if response.status_code == 401:
            return {}

        response.raise_for_status()
        return response.json()

    def _create_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data creation methods."""

        def create_record(**data) -> None:
            """Create an API record.

            Args:
                **data: New record values.

            Returns:
                A copy of the created record.
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
                order: Optionally order returned values by the given parameter.
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


class AsyncKeystoneClient(ClientBase, AsyncHTTPClient):
    """Client class for submitting asynchronous requests to the Keystone API."""

    async def login(self, username: str, password: str, timeout: int = DEFAULT_TIMEOUT) -> None:
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

    async def logout(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Logout the current user session.

        Args:
            timeout: Seconds before the request times out.
        """

        response = await self.http_post(
            endpoint=self.LOGOUT_ENDPOINT,
            timeout=timeout
        )

        response.raise_for_status()

    async def is_authenticated(self, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """Return metadata for the currently authenticated user.

        Returns an empty dictionary if the current session is not authenticated.

        Args:
            timeout: Seconds before the request times out.
        """

        response = await self.http_get(self.IDENTITY_ENDPOINT, timeout=timeout)
        if response.status_code == 401:
            return {}

        response.raise_for_status()
        return response.json()

    def _create_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data creation methods."""

        async def create_record(**data) -> None:
            """Create an API record.

            Args:
                **data: New record values.

            Returns:
                A copy of the created record.
            """

            url = endpoint.join_url(self.base_url)
            response = await self.http_post(url, json=data)
            response.raise_for_status()
            return response.json()

        return create_record

    def _retrieve_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data retrieval methods."""

        async def retrieve_record(
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
                order: Optionally order returned values by the given parameter.
                timeout: Seconds before the request times out.

            Returns:
                The data record(s) or None.
            """

            url = endpoint.join_url(self.base_url, pk)

            for param_name, value in zip(('_search', '_order'), (search, order)):
                if value is not None:
                    filters = filters or {}
                    filters[param_name] = value

            response = await self.http_get(url, params=filters, timeout=timeout)

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

        async def update_record(pk: int, data: dict) -> dict:
            """Update an API record.

            Args:
                pk: Primary key of the record to update.
                data: New record values.

            Returns:
                A copy of the updated record.
            """

            url = endpoint.join_url(self.base_url, pk)
            response = await self.http_patch(url, json=data)
            response.raise_for_status()
            return response.json()

        return update_record

    def _delete_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data deletion methods."""

        async def delete_record(pk: int, raise_not_exists: bool = False) -> None:
            """Delete an API record.

            Args:
                pk: Primary key of the record to delete.
                raise_not_exists: Raise an error if the record does not exist.
            """

            url = endpoint.join_url(self.base_url, pk)
            response = await self.http_delete(url)

            try:
                response.raise_for_status()

            except httpx.HTTPError:
                if response.status_code == 404 and not raise_not_exists:
                    return

                raise

        return delete_record
