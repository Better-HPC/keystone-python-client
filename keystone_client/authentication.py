"""User authentication and credential management."""

from __future__ import annotations

from datetime import datetime

import jwt
import requests


class JWT:
    """JWT authentication tokens"""

    def __init__(self, access: str, refresh: str, algorithm='HS256') -> None:
        """Initialize a new pair of JWT tokens

        Args:
            access: The access token
            refresh: The refresh token
        """

        self.access = access
        self.refresh = refresh
        self.algorithm = algorithm

    @property
    def access_expiration(self) -> datetime:
        """Return the expiration datetime of the JWT access token"""

        token_data = jwt.decode(self.access, options={"verify_signature": False}, algorithms=self.algorithm)
        return datetime.fromtimestamp(token_data["exp"])

    @property
    def refresh_expiration(self) -> datetime:
        """Return the expiration datetime of the JWT refresh token"""

        token_data = jwt.decode(self.refresh, options={"verify_signature": False}, algorithms=self.algorithm)
        return datetime.fromtimestamp(token_data["exp"])


class AuthenticationManager:
    """User authentication and JWT token manager"""

    default_timeout = 15

    def __init__(self, auth_url: str, refresh_url: str, blacklist_url: str) -> None:
        """Initialize the class

        Args:
            auth_url: API URL for fetching new JWT tokens
            refresh_url: API URL for refreshing JWT tokens
            blacklist_url: API URL for blacklisting JWT tokens
        """

        self.auth_url = auth_url
        self.refresh_url = refresh_url
        self.blacklist_url = blacklist_url
        self.jwt: JWT | None = None

    def is_authenticated(self) -> bool:
        """Return whether the client instance has been authenticated"""

        if self.jwt is None:
            return False

        now = datetime.now()
        access_token_valid = self.jwt.access_expiration > now
        access_token_refreshable = self.jwt.refresh_expiration > now
        return access_token_valid or access_token_refreshable

    def get_auth_headers(self) -> dict[str, str]:
        """Return header data for API requests

        Returns:
            A dictionary with header data
        """

        if not self.is_authenticated():
            raise ValueError('User session is not authenticated')

        self.refresh()
        return {
            "Authorization": f"Bearer {self.jwt.access}",
            "Content-Type": "application/json"
        }

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
            self.auth_url,
            json={"username": username, "password": password},
            timeout=timeout
        )

        response.raise_for_status()
        response_data = response.json()
        self.jwt = JWT(response_data.get("access"), response_data.get("refresh"))

    def logout(self, timeout: int = default_timeout) -> None:
        """Log out and blacklist any active JWTs

        Args:
            timeout: Seconds before the request times out
        """

        # Tell the API to blacklist the current token
        if self.jwt is not None:
            response = requests.post(
                self.blacklist_url,
                data={"refresh": self.jwt.refresh},
                timeout=timeout
            )

            response.raise_for_status()

        self.jwt = None

    def refresh(self, force: bool = False, timeout: int = default_timeout) -> None:
        """Refresh the JWT access token

        Args:
            timeout: Seconds before the request times out
            force: Refresh the access token even if it has not expired yet
        """

        if not self.is_authenticated:
            return

        # Don't refresh the token if it's not necessary
        now = datetime.now()
        if self.jwt.access_expiration > now and not force:
            return

        # Alert the user when a refresh is not possible
        if self.jwt.refresh_expiration > now:
            raise RuntimeError("Refresh token has expired. Login again to continue.")

        response = requests.post(
            self.refresh_url,
            data={"refresh": self.jwt.refresh},
            timeout=timeout
        )

        response.raise_for_status()
        self.jwt.refresh = response.json().get("refresh")
