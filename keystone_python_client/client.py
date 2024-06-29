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
