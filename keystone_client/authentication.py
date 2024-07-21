"""User authentication and credential management."""

from __future__ import annotations

from datetime import datetime

import jwt
import requests

from keystone_client.schema import AuthSchema


class JWT:
    """JWT authentication tokens"""

    def __init__(self, access: str, refresh: str, algorithm='HS256') -> None:
        """Initialize a new pair of JWT tokens

        Args:
            access: The access token
            refresh: The refresh token
            algorithm: The algorithm used for encoding the JWT
        """

        self.algorithm = algorithm
        self.access = access
        self.refresh = refresh

    def _decode_token(self, token: str) -> tuple[str, datetime]:
        """Decode a JWT token and return the token and its expiration datetime"""

        token_data = jwt.decode(token, options={"verify_signature": False}, algorithms=self.algorithm)
        exp = datetime.fromtimestamp(token_data["exp"])
        return token, exp

    @property
    def access(self) -> str:
        """Return the JWT access token"""

        return self._access_token

    @access.setter
    def access(self, value: str) -> None:
        """Set the JWT access token"""

        self._access_token, self._access_exp = self._decode_token(value)

    @property
    def access_expiration(self) -> datetime:
        """Return the expiration datetime of the JWT access token"""

        return self._access_exp

    @property
    def refresh(self) -> str:
        """Return the JWT refresh token"""

        return self._refresh_token

    @refresh.setter
    def refresh(self, value: str) -> None:
        """Set the JWT refresh token"""

        self._refresh_token, self._refresh_exp = self._decode_token(value)

    @property
    def refresh_expiration(self) -> datetime:
        """Return the expiration datetime of the JWT refresh token"""

        return self._refresh_exp


class AuthenticationManager:
    """User authentication and JWT token manager"""

    default_timeout = 15

    def __init__(self, url: str, schema: AuthSchema = AuthSchema()) -> None:
        """Initialize the class

        Args:
            url: Base URL for the authentication API
            schema: Schema defining API endpoints for fetching/managing JWTs
        """

        self.auth_url = schema.new.resolve(url)
        self.refresh_url = schema.refresh.resolve(url)
        self.blacklist_url = schema.blacklist.resolve(url)
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
