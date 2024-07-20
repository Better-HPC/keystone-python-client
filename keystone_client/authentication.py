"""User authentication and credential management."""

from __future__ import annotations

from datetime import datetime

import jwt
import requests


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

        # Attributes to hold JWT data
        self._access_token: str | None = None
        self._refresh_token: str | None = None

    @property
    def access_token(self) -> str | None:
        """Return the JWT access token"""

        return self._access_token

    @property
    def access_expiration(self) -> datetime | None:
        """Return the expiration datetime of the JWT access token"""

        if self.access_token:
            return datetime.fromtimestamp(jwt.decode(self.access_token)["exp"])

    @property
    def refresh_token(self) -> str | None:
        """Return the JWT refresh token"""

        return self._refresh_token

    @property
    def refresh_expiration(self) -> datetime | None:
        """Return the expiration datetime of the JWT refresh token"""

        if self.refresh_token:
            return datetime.fromtimestamp(jwt.decode(self.refresh_token)["exp"])

    def is_authenticated(self) -> None:
        """Return whether the client instance has been authenticated"""

        now = datetime.now()
        has_token = self.refresh_token is not None
        access_token_valid = self.access_expiration is not None and self.access_expiration > now
        access_token_refreshable = self.refresh_expiration is not None and self.refresh_expiration > now
        return has_token and (access_token_valid or access_token_refreshable)

    def get_auth_headers(self) -> dict[str, str]:
        """Return header data for API requests

        Returns:
            A dictionary with header data
        """

        if not self.access_token:
            return dict()

        self.refresh()
        return {
            "Authorization": f"Bearer {self.access_token}",
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

        json = response.json()
        self._refresh_token = json.get("refresh")
        self._access_token = json.get("access")

    def logout(self, timeout: int = default_timeout) -> None:
        """Log out and blacklist any active JWTs

        Args:
            timeout: Seconds before the request times out
        """

        # Tell the API to blacklist the current token
        if self._refresh_token is not None:
            response = requests.post(
                self.blacklist_url,
                data={"refresh": self._refresh_token},
                timeout=timeout
            )

            response.raise_for_status()

        # Clear invalidated token data
        self._refresh_token = None
        self._access_token = None

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
        if self.access_expiration > now and not force:
            return

        # Alert the user when a refresh is not possible
        if self.refresh_expiration > now:
            raise RuntimeError("Refresh token has expired. Login again to continue.")

        response = requests.post(
            self.refresh_url,
            data={"refresh": self._refresh_token},
            timeout=timeout
        )

        response.raise_for_status()
        self._refresh_token = response.json().get("refresh")
