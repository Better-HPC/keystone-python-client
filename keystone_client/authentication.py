"""User authentication and credential management."""

from __future__ import annotations

from datetime import datetime
from warnings import warn

import jwt
import requests

from keystone_client.schema import Schema


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

    def _date_from_token(self, token: str) -> datetime:
        """Return a token's expiration datetime"""

        token_data = jwt.decode(token, options={"verify_signature": False}, algorithms=self.algorithm)
        exp = datetime.fromtimestamp(token_data["exp"])
        return exp

    @property
    def access_expiration(self) -> datetime:
        """Return the expiration datetime of the JWT access token"""

        return self._date_from_token(self.access)

    @property
    def refresh_expiration(self) -> datetime:
        """Return the expiration datetime of the JWT refresh token"""

        return self._date_from_token(self.refresh)


class AuthenticationManager:
    """User authentication and JWT token manager"""

    def __init__(self, url: str, schema: Schema = Schema()) -> None:
        """Initialize the class

        Args:
            url: Base URL for the authentication API
            schema: Schema defining API endpoints for fetching/managing JWTs
        """

        self.jwt: JWT | None = None
        self.auth_url = schema.auth.new.join_url(url)
        self.refresh_url = schema.auth.refresh.join_url(url)
        self.blacklist_url = schema.auth.blacklist.join_url(url)

    def is_authenticated(self) -> bool:
        """Return whether the client instance has active credentials"""

        if self.jwt is None:
            return False

        now = datetime.now()
        access_token_valid = self.jwt.access_expiration > now
        access_token_refreshable = self.jwt.refresh_expiration > now
        return access_token_valid or access_token_refreshable

    def get_auth_headers(self, refresh: bool = True, timeout: int = None) -> dict[str, str]:
        """Return headers data for authenticating API requests

        The returned dictionary is empty when not authenticated.

        Args:
            refresh: Automatically refresh the JWT credentials if necessary
            timeout: Seconds before the token refresh request times out

        Returns:
            A dictionary with header ata for JWT authentication
        """

        if refresh:
            self.refresh(timeout=timeout)

        if not self.is_authenticated():
            return dict()

        return {"Authorization": f"Bearer {self.jwt.access}"}

    def login(self, username: str, password: str, timeout: int = None) -> None:
        """Log in to the Keystone API and cache the returned credentials

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

    def logout(self, timeout: int = None) -> None:
        """Log out of the current session and blacklist any current credentials

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

            try:
                response.raise_for_status()

            except Exception as error:
                warn(f"Token blacklist request failed: {error}")

        self.jwt = None

    def refresh(self, force: bool = False, timeout: int = None) -> None:
        """Refresh the current session credetials if necessary

        This method will do nothing and exit silently if the current session
        has not been authenticated.

        Args:
            timeout: Seconds before the request times out
            force: Refresh the access token even if it has not expired yet
        """

        if self.jwt is None:
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
