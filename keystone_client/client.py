"""Keystone API Client

This module provides a client class `KeystoneAPIClient` for interacting with the
Keystone API. It streamlines communication with the API, providing methods for
authentication, data retrieval, and data manipulation.
"""

from __future__ import annotations

from functools import partial
from typing import Literal, Union

import requests

from keystone_client.http import HTTPClient

# Custom types
ContentType = Literal["json", "text", "content"]
ResponseContent = Union[dict[str, any], str, bytes]
QueryResult = Union[None, dict, list[dict]]


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
        for key, endpoint in zip(cls.schema._fields, cls.schema):

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
