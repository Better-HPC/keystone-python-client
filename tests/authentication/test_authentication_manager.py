"""Tests for the `AuthenticationManager` class."""

from datetime import datetime, timedelta
from unittest import TestCase

import jwt
from requests.exceptions import HTTPError

from keystone_client.authentication import AuthenticationManager, JWT
from tests import API_HOST, API_PASSWORD, API_USER


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


class IsAuthenticated(TestCase):
    """Tests for the `is_authenticated` method"""

    def test_not_authenticated(self) -> None:
        """Test the return value is `false` when the manager has no JWT data"""

        manager = AuthenticationManager(API_HOST)
        self.assertIsNone(manager.jwt)
        self.assertFalse(manager.is_authenticated())

    def test_valid_jwt(self) -> None:
        """Test the return value is `True` when the JWT token is not expired"""

        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() + timedelta(hours=1),
            refresh_expires=datetime.now() + timedelta(days=1)
        )

        self.assertTrue(manager.is_authenticated())

    def test_refreshable_jwt(self) -> None:
        """Test the return value is `True` when the JWT token expired but refreshable"""

        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() - timedelta(hours=1),
            refresh_expires=datetime.now() + timedelta(days=1)
        )

        self.assertTrue(manager.is_authenticated())

    def test_expired_jwt(self) -> None:
        """Test the return value is `False` when the JWT token is expired"""

        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() - timedelta(days=1),
            refresh_expires=datetime.now() - timedelta(hours=1)
        )

        self.assertFalse(manager.is_authenticated())


class GetAuthHeaders(TestCase):
    """Tests for the `get_auth_headers` method"""

    def test_not_authenticated(self) -> None:
        """Test the returned headers are empty when not authenticated"""

        manager = AuthenticationManager(API_HOST)
        headers = manager.get_auth_headers()
        self.assertEqual(dict(), headers)

    def test_headers_match_jwt(self) -> None:
        """Test the returned data matches the JWT token"""

        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() + timedelta(hours=1),
            refresh_expires=datetime.now() + timedelta(days=1)
        )

        headers = manager.get_auth_headers()
        self.assertEqual(f"Bearer {manager.jwt.access}", headers["Authorization"])


class LoginLogout(TestCase):
    """Test the logging in/out of users"""

    def test_correct_credentials(self) -> None:
        """Test users are successfully logged in/out when providing correct credentials"""

        manager = AuthenticationManager(API_HOST)
        self.assertFalse(manager.is_authenticated())

        manager.login(API_USER, API_PASSWORD)
        self.assertTrue(manager.is_authenticated())

        manager.logout()
        self.assertFalse(manager.is_authenticated())

    def test_incorrect_credentials(self) -> None:
        """Test an error is raised when authenticating with invalid credentials"""

        manager = AuthenticationManager(API_HOST)
        with self.assertRaises(HTTPError) as error:
            manager.login('foo', 'bar')
            self.assertEqual(401, error.response.status_code)
