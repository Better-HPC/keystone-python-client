"""Keystone API Client

This module provides a client class `KeystoneAPIClient` for interacting with the
Keystone API. It streamlines communication with the API, providing methods for
authentication, data retrieval, and data manipulation.
"""

from __future__ import annotations, annotations

from functools import partial
from typing import Literal, Union

import requests

from keystone_client.authentication import AuthenticationManager
from keystone_client.schema import Endpoint, Schema

# Custom types
ContentType = Literal["json", "text", "content"]
ResponseContent = Union[dict[str, any], str, bytes]
QueryResult = Union[None, dict, list[dict]]
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
        self._auth = AuthenticationManager(url, self.schema.auth)
        self._api_version: str | None = None

    @property
    def url(self) -> str:
        """Return the server URL"""

        return self._url

    def _send_request(self, method: HTTPMethod, endpoint: str, **kwargs) -> requests.Response:
        """Send an HTTP request

        Args:
            method: The HTTP method to use
            endpoint: The complete url to send the request to
            timeout: Seconds before the request times out

        Returns:
            An HTTP response
        """

        url = Endpoint(endpoint).resolve(self.url)
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


class KeystoneClient(HTTPClient):
    """Client class for submitting requests to the Keystone API"""

    default_timeout = 15

    @property
    def api_version(self) -> str:
        """Return the version number of the API server"""

        if self._api_version is None:
            response = self.http_get("version")
            response.raise_for_status()
            self._api_version = response.text

        return self._api_version

    def __new__(cls, *args, **kwargs) -> KeystoneClient:
        """Dynamically create CRUD methods for each endpoint in the API schema

        Dynamic method are only generated of they do not already implemented
        in the class definition.
        """

        instance: KeystoneClient = super().__new__(cls)
        for key, endpoint in cls.schema.data.dict().items():

            # Create a retrieve method
            retrieve_name = f"retrieve_{key}"
            if not hasattr(instance, retrieve_name):
                retrieve_method = partial(instance._retrieve_records, _endpoint=endpoint)
                setattr(instance, f"retrieve_{key}", retrieve_method)

        return instance

    def _retrieve_records(
        self,
        _endpoint: str,
        pk: int | None = None,
        filters: dict | None = None,
        timeout=default_timeout
    ) -> QueryResult:
        """Retrieve data from the specified endpoint with optional primary key and filters

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

        if pk is not None:
            _endpoint = f"{_endpoint}/{pk}/"

        try:
            response = self.http_get(_endpoint, params=filters, timeout=timeout)
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as exception:
            if exception.response.status_code == 404:
                return None

            raise
