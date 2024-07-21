"""Tests for the `AuthenticationManager` class."""

from datetime import datetime, timedelta
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
        """Test the return value is `True` when the JWT token is not expired"""

        manager = AuthenticationManager('auth', 'refresh', 'blacklist')
        manager.jwt = self.create_token(
            access_expires=datetime.now() + timedelta(hours=1),
            refresh_expires=datetime.now() + timedelta(days=1)
        )

        self.assertTrue(manager.is_authenticated())

    def test_refreshable_jwt(self) -> None:
        """Test the return value is `True` when the JWT token expired but refreshable"""

        manager = AuthenticationManager('auth', 'refresh', 'blacklist')
        manager.jwt = self.create_token(
            access_expires=datetime.now() - timedelta(hours=1),
            refresh_expires=datetime.now() + timedelta(days=1)
        )

        self.assertTrue(manager.is_authenticated())

    def test_expired_jwt(self) -> None:
        """Test the return value is `False` when the JWT token expired"""

        manager = AuthenticationManager('auth', 'refresh', 'blacklist')
        manager.jwt = self.create_token(
            access_expires=datetime.now() - timedelta(days=1),
            refresh_expires=datetime.now() - timedelta(hours=1)
        )

        self.assertFalse(manager.is_authenticated())
