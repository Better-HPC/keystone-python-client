from typing import *

__all__ = ["KeystoneClient"]

from warnings import warn

import requests


class KeystoneClient:
    """Client class for submitting requests to the Keystone API"""

    # Default API behavior
    default_timeout = 15

    # API endpoints
    authentication_new = "authentication/new/"
    authentication_blacklist = "authentication/blacklist/"

    def __init__(self, url: str) -> None:
        """Initialize the class

        Args:
            url: The base API URL
        """

        self.url = url
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

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

        except Exception as excep:
            warn(str(excep))

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
            timeout: Number of seconds before the requests times out

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
            timeout: Number of seconds before the requests times out

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
            timeout: Number of seconds before the requests times out

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
            timeout: Number of seconds before the requests times out

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
            timeout: Number of seconds before the requests times out

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
