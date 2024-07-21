"""Tests for the `JWT` class."""

import unittest
from datetime import datetime, timedelta

import jwt

from keystone_client.authentication import JWT


class TokenParsing(unittest.TestCase):
    """Test JWT token parsing"""

    def setUp(self) -> None:
        """Create a JWT token for testing"""

        self.access_expiration = datetime.now() + timedelta(hours=1)
        self.access_token = jwt.encode({'exp': self.access_expiration.timestamp()}, 'secret', algorithm='HS256')

        self.refresh_expiration = datetime.now() + timedelta(days=1)
        self.refresh_token = jwt.encode({'exp': self.refresh_expiration.timestamp()}, 'secret', algorithm='HS256')
        self.jwt = JWT(self.access_token, self.refresh_token)

    def test_access_token(self) -> None:
        """Test the access token is returned"""

        self.assertEqual(self.jwt.access, self.access_token)

    def test_access_expiration(self) -> None:
        """Test the access token expiration date is returned"""

        self.assertEqual(self.access_expiration, self.jwt.access_expiration)

    def test_refresh_token(self) -> None:
        """Test the refresh token is returned"""

        self.assertEqual(self.jwt.refresh, self.refresh_token)

    def test_refresh_expiration(self) -> None:
        """Test the refresh token expiration date is returned"""

        self.assertEqual(self.refresh_expiration, self.jwt.refresh_expiration)
