from __future__ import annotations

from collections import namedtuple
from functools import partial
from typing import *
from warnings import warn

import requests

__all__ = ["KeystoneClient"]

# Custom types
ContentType = Literal['json', 'text', 'content']
ResponseContent = Union[Dict[str, Any], str, bytes]
QueryResult = Union[None, dict, List[dict]]

# API schema mapping human-readable, python-friendly names to API endpoints
Schema = namedtuple('Schema', [
    'allocations',
    'requests',
    'research_groups',
    'users',
])


class KeystoneClient:
    """Client class for submitting requests to the Keystone API"""

    # Default API behavior
    default_timeout = 15

    # API endpoints
    authentication_new = "authentication/new/"
    authentication_blacklist = "authentication/blacklist/"
    schema = Schema(
        allocations='allocations/allocations/',
        requests='allocations/requests/',
        research_groups='users/researchgroups/',
        users='users/users/',
    )

    def __init__(self, url: str) -> None:
        """Initialize the class

        Args:
            url: The base API URL
        """

        self.url = url
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

    def __new__(cls, *args, **kwargs) -> KeystoneClient:
        """Dynamically create CRUD methods for each endpoint in the API schema"""

        instance: KeystoneClient = super().__new__(cls)
        for key, endpoint in zip(cls.schema._fields, cls.schema):
            new_method = partial(instance._retrieve_records, _endpoint=endpoint)
            setattr(instance, f'retrieve_{key}', new_method)

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
            timeout: Number of seconds before the request times out

        Returns:
            The response from the API in JSON format
        """

        if pk is not None:
            _endpoint = f'{_endpoint}/{pk}/'

        try:
            response = self.http_get(_endpoint, params=filters, timeout=timeout)
            return response.json()

        except requests.HTTPError as exception:
            if exception.response.status_code == 404:
                return None

            raise

    @property
    def access_token(self) -> Union[str, None]:
        """Return the JSON access token"""

        return self._access_token

    @property
    def refresh_token(self) -> Union[str, None]:
        """Return the JSON refresh token"""

        return self._refresh_token

    def login(self, username: str, password: str, timeout: int = default_timeout) -> None:
        """Log in to the Keystone API and cache the returned JWT

        Args:
            username: The authentication username
            password: The authentication password
            timeout: Seconds before the requests times out

        Raises:
            requests.HTTPError: If the login request fails
        """

        response = requests.post(
            f"{self.url}/{self.authentication_new}",
            json={"username": username, "password": password},
            timeout=timeout
        )

        response.raise_for_status()
        self._refresh_token = response.json().get("refresh")
        self._access_token = response.json().get("access")

    def logout(self, timeout: int = default_timeout) -> None:
        """Log out and blacklist any active JWTs

        Args:
            timeout: Seconds before the requests times out
        """

        response = requests.post(
            f"{self.url}/{self.authentication_blacklist}",
            data={"refresh": self.refresh_token},
            timeout=timeout
        )

        try:
            response.raise_for_status()

        except Exception as exception:
            warn(str(exception))

        self._refresh_token = None
        self._access_token = None

    def _get_headers(self) -> Dict[str, str]:
        """Return header data for API requests

        Returns:
            A dictionary with header data
        """

        if not self._access_token:
            return dict()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

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
            timeout: Number of seconds before the request times out

        Returns:
            The response from the API in the specified format

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        response = requests.get(
            f"{self.url}/{endpoint}",
            headers=self._get_headers(),
            params=params,
            timeout=timeout
        )

        response.raise_for_status()
        return response

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
            timeout: Number of seconds before the request times out

        Returns:
            The response from the API in the specified format

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        response = requests.post(
            f"{self.url}/{endpoint}",
            headers=self._get_headers(),
            json=data,
            timeout=timeout
        )

        response.raise_for_status()
        return response

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
            timeout: Number of seconds before the request times out

        Returns:
            The response from the API in the specified format

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        response = requests.patch(
            f"{self.url}/{endpoint}",
            headers=self._get_headers(),
            json=data,
            timeout=timeout
        )

        response.raise_for_status()
        return response

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
            timeout: Number of seconds before the request times out

        Returns:
            The API response

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        response = requests.put(
            f"{self.url}/{endpoint}",
            headers=self._get_headers(),
            json=data,
            timeout=timeout
        )

        response.raise_for_status()
        return response

    def http_delete(
        self,
        endpoint: str,
        timeout: int = default_timeout
    ) -> requests.Response:
        """Send a DELETE request to an endpoint

        Args:
            endpoint: API endpoint to send the request to
            timeout: Number of seconds before the request times out

        Returns:
            The API response

        Raises:
            requests.HTTPError: If the request returns an error code
        """

        response = requests.delete(
            f"{self.url}/{endpoint}",
            headers=self._get_headers(),
            timeout=timeout
        )

        response.raise_for_status()
        return response
