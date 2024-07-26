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

from keystone_client.authentication import AuthenticationManager
from keystone_client.schema import Endpoint, Schema

DEFAULT_TIMEOUT = 15

# Custom types
ContentType = Literal["json", "text", "content"]
ResponseContent = Union[dict[str, any], str, bytes]
QueryResult = Union[None, dict, list[dict]]
HTTPMethod = Literal["get", "post", "put", "patch", "delete"]


class HTTPClient:
    """Low level API client for sending standard HTTP operations"""

    schema = Schema()

    def __init__(self, url: str) -> None:
        """Initialize the class

        Args:
            url: The base URL for a running Keystone API server
        """

        self._url = url.rstrip('/') + '/'
        self._auth = AuthenticationManager(url, self.schema)

    @property
    def url(self) -> str:
        """Return the server URL"""

        return self._url

    def login(self, username: str, password: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Authenticate a new user session

        Args:
            username: The authentication username
            password: The authentication password
            timeout: Seconds before the request times out

        Raises:
            requests.HTTPError: If the login request fails
        """

        self._auth.login(username, password, timeout)  # pragma: nocover

    def logout(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Log out and blacklist any active credentials

        Args:
            timeout: Seconds before the blacklist request times out
        """

        self._auth.logout(timeout)  # pragma: nocover

    def is_authenticated(self) -> bool:
        """Return whether the client instance has active credentials"""

        return self._auth.is_authenticated()  # pragma: nocover

    def _send_request(self, method: HTTPMethod, endpoint: str, **kwargs) -> requests.Response:
        """Send an HTTP request

        Args:
            method: The HTTP method to use
            endpoint: The complete url to send the request to
            timeout: Seconds before the request times out

        Returns:
            An HTTP response
        """

        url = urljoin(self.url, endpoint)
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def http_get(
        self,
        endpoint: str,
        params: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
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

        return self._send_request(
            "get",
            endpoint,
            params=params,
            headers=self._auth.get_auth_headers(),
            timeout=timeout
        )

    def http_post(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
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

        return self._send_request(
            "post",
            endpoint,
            data=data,
            headers=self._auth.get_auth_headers(),
            timeout=timeout
        )

    def http_patch(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
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

        return self._send_request(
            "patch",
            endpoint,
            data=data,
            headers=self._auth.get_auth_headers(),
            timeout=timeout
        )

    def http_put(
        self,
        endpoint: str,
        data: dict[str, any] | None = None,
        timeout: int = DEFAULT_TIMEOUT
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

        return self._send_request(
            "put",
            endpoint,
            data=data,
            headers=self._auth.get_auth_headers(),
            timeout=timeout
        )

    def http_delete(
        self,
        endpoint: str,
        timeout: int = DEFAULT_TIMEOUT
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

        return self._send_request(
            "delete",
            endpoint,
            headers=self._auth.get_auth_headers(),
            timeout=timeout
        )


class KeystoneClient(HTTPClient):
    """Client class for submitting requests to the Keystone API"""

    @cached_property
    def api_version(self) -> str:
        """Return the version number of the API server"""

        response = self.http_get("version")
        response.raise_for_status()
        return response.text

    def __new__(cls, *args, **kwargs) -> KeystoneClient:
        """Dynamically create CRUD methods for each data endpoint in the API schema"""

        new: KeystoneClient = super().__new__(cls)

        new.retrieve_allocation = new._retrieve_factory(cls.schema.data.allocations)
        new.retrieve_request = new._retrieve_factory(cls.schema.data.requests)
        new.retrieve_research_group = new._retrieve_factory(cls.schema.data.research_groups)
        new.retrieve_user = new._retrieve_factory(cls.schema.data.users)

        return new

    def _create_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data creation methods"""

        def create_record(**kwargs) -> None:
            url = endpoint.join_url(self.url)
            response = self.http_post(url, data=kwargs)
            response.raise_for_status()
            return response.json()

        return create_record

    def _retrieve_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data retrieval methods"""

        def retrieve_record(
            pk: int | None = None,
            filters: dict | None = None,
            timeout=DEFAULT_TIMEOUT
        ) -> QueryResult:
            """Retrieve data from the API endpoint with optional primary key and filters

            A single record is returned when specifying a primary key, otherwise the returned
            object is a list of records. In either case, the return value is `None` when no data
            is available for the query.

            Args:
                pk: Optional primary key to fetch a specific record
                filters: Optional query parameters to include in the request
                timeout: Seconds before the request times out

            Returns:
                The response from the API in JSON format
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
        """Factory function for data update methods"""

        def update_record(pk: int, **kwargs) -> dict:
            url = endpoint.join_url(self.url, pk)
            response = self.http_patch(url, data=kwargs)
            response.raise_for_status()
            return response.json()

        return update_record

    def _delete_factory(self, endpoint: Endpoint) -> callable:
        """Factory function for data deletion methods"""

        def delete_record(pk: int) -> None:
            url = endpoint.join_url(self.url, pk)
            response = self.http_delete(url)
            response.raise_for_status()

        return delete_record
