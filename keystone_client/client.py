from __future__ import annotations

from collections import namedtuple
from datetime import datetime
from functools import partial
from typing import *
from warnings import warn

import jwt
import requests

__all__ = ["KeystoneAPIClient"]

# Custom types
ContentType = Literal["json", "text", "content"]
ResponseContent = Union[Dict[str, Any], str, bytes]
QueryResult = Union[None, dict, List[dict]]
HTTPMethod = Literal["get", "post", "put", "patch", "delete"]

# API schema mapping human-readable, python-friendly names to API endpoints
Schema = namedtuple("Schema", [
    "allocations",
    "requests",
    "research_groups",
    "users",
])


class KeystoneAPIClient:
    """Client class for submitting requests to the Keystone API"""

    # Default API behavior
    default_timeout = 15

    # API endpoints
    authentication_new = "authentication/new/"
    authentication_blacklist = "authentication/blacklist/"
    authentication_refresh = "authentication/refresh/"
    schema = Schema(
        allocations="allocations/allocations/",
        requests="allocations/requests/",
        research_groups="users/researchgroups/",
        users="users/users/",
    )

    def __init__(self, url: str, auto_refresh: bool = True) -> None:
        """Initialize the class

        Args:
            url: The base URL for a running Keystone API server
            auto_refresh: Automatically refresh authentication tokens
        """

        self.url = url
        self.auto_refresh = auto_refresh

        self._api_version: Optional[str] = None
        self._access_token: Optional[str] = None
        self._access_expiration: Optional[datetime] = None
        self._refresh_token: Optional[str] = None
        self._refresh_expiration: Optional[datetime] = None

    def __new__(cls, *args, **kwargs) -> KeystoneAPIClient:
        """Dynamically create CRUD methods for each endpoint in the API schema

        Dynamic method are only generated of they do not already implemented
        in the class definition.
        """

        instance: KeystoneAPIClient = super().__new__(cls)
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
        pk: Optional[int] = None,
        filters: Optional[dict] = None,
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

    def _get_headers(self) -> Dict[str, str]:
        """Return header data for API requests

        Returns:
            A dictionary with header data
        """

        if not self._access_token:
            return dict()

        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

    def _send_request(self, method: HTTPMethod, url: str, timeout: int = default_timeout, **kwargs) -> requests.Response:
        """Send an HTTP request

        Args:
            method: The HTTP method to use
            url: The complete url to send the request to
            timeout: Seconds before the request times out

        Returns:
            An HTTP response
        """

        if self.auto_refresh:
            self._refresh_tokens(force=False, timeout=timeout)

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def http_get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
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
        data: Optional[Dict[str, Any]] = None,
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
        data: Optional[Dict[str, Any]] = None,
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
        data: Optional[Dict[str, Any]] = None,
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

    @property
    def is_authenticated(self) -> None:
        """Return whether the client instance has been authenticated"""

        now = datetime.now()
        has_token = self._refresh_token is not None
        access_token_valid = self._access_expiration > now
        access_token_refreshable = self._refresh_expiration > now
        return has_token and (access_token_valid or access_token_refreshable)

    @property
    def api_version(self) -> str:
        """Return the version number of the API server"""

        if self._api_version is None:
            response = self.http_get("version")
            response.raise_for_status()
            self._api_version = response.text

        return self._api_version

    def login(self, username: str, password: str, timeout: int = default_timeout) -> None:
        """Log in to the Keystone API and cache the returned JWT

        Args:
            username: The authentication username
            password: The authentication password
            timeout: Seconds before the request times out

        Raises:
            requests.HTTPError: If the login request fails
        """

        response = requests.post(
            f"{self.url}/{self.authentication_new}",
            json={"username": username, "password": password},
            timeout=timeout
        )

        response.raise_for_status()

        # Parse data from the refresh token
        refresh_payload = jwt.decode(self._refresh_token, options={"verify_signature": False})
        self._refresh_token = response.json().get("refresh")
        self._refresh_expiration = datetime.fromtimestamp(refresh_payload["exp"])

        # Parse data from the access token
        access_payload = jwt.decode(self._access_token, options={"verify_signature": False})
        self._access_token = response.json().get("access")
        self._access_expiration = datetime.fromtimestamp(access_payload["exp"])

    def logout(self, timeout: int = default_timeout) -> None:
        """Log out and blacklist any active JWTs

        Args:
            timeout: Seconds before the request times out
        """

        if self._refresh_token is not None:
            response = requests.post(
                f"{self.url}/{self.authentication_blacklist}",
                data={"refresh": self._refresh_token},
                timeout=timeout
            )

            try:
                response.raise_for_status()

            except Exception as exception:
                warn(str(exception))

        self._refresh_token = None
        self._refresh_expiration = None
        self._access_token = None
        self._access_expiration = None

    def _refresh_tokens(self, force: bool = True, timeout: int = default_timeout) -> None:
        """Refresh the JWT access token

        Args:
            timeout: Seconds before the request times out
            force: Refresh the access token even if it has not expired yet
        """

        # Don't refresh the token if it's not necessary
        now = datetime.now()
        if self._access_expiration > now and not force:
            return

        # Alert the user when a refresh is not possible
        if self._refresh_expiration > now:
            raise RuntimeError("Refresh token has expired. Login again to continue.")

        response = requests.post(
            f"{self.url}/{self.authentication_refresh}",
            data={"refresh": self._refresh_token},
            timeout=timeout
        )

        response.raise_for_status()
        refresh_payload = jwt.decode(self._refresh_token, options={"verify_signature": False})
        self._refresh_token = response.json().get("refresh")
        self._refresh_expiration = datetime.fromtimestamp(refresh_payload["exp"])
