"""Tests for the `AuthenticationManager` class."""

from datetime import datetime
from unittest import TestCase

import jwt

from keystone_client.authentication import AuthenticationManager, JWT


class IsAuthenticated(TestCase):
    """Tests for the `is_authenticated` method"""

    @staticmethod
    def create_token(access_expires: datetime, refresh_expires: datetime) -> JWT:
        """Create a JWT token

        Args:
            access_expires: The expiration datetime for the access token
            refresh_expires: The expiration datetime for the refresh token

        Returns:
            A JWT instance with the given expiration dates
        """

        return JWT(
            access=jwt.encode({'exp': access_expires.timestamp()}, 'secret'),
            refresh=jwt.encode({'exp': refresh_expires.timestamp()}, 'secret')
        )

    def test_not_authenticated(self) -> None:
        """Test the return value is `false` when the manager has no JWT data"""

        manager = AuthenticationManager('auth', 'refresh', 'blacklist')
        self.assertIsNone(manager.jwt)
        self.assertFalse(manager.is_authenticated())

    def test_valid_jwt(self) -> None:
        self.fail()

    def test_expired_jwt(self) -> None:
        self.fail()
