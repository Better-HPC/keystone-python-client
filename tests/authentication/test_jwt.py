"""Tests for the `JWT` class."""

from datetime import datetime, timedelta
from unittest import TestCase

import jwt

from keystone_client.authentication import JWT


class BaseTests:
    """Base class containing reusable tests"""

    algorithm: str

    @classmethod
    def setUpClass(cls) -> None:
        """Test the parsing of JWT data"""

        # Build a JWT
        cls.access_expiration = datetime.now() + timedelta(hours=1)
        cls.access_token = jwt.encode({'exp': cls.access_expiration.timestamp()}, 'secret', algorithm=cls.algorithm)

        cls.refresh_expiration = datetime.now() + timedelta(days=1)
        cls.refresh_token = jwt.encode({'exp': cls.refresh_expiration.timestamp()}, 'secret', algorithm=cls.algorithm)

        cls.jwt = JWT(cls.access_token, cls.refresh_token, cls.algorithm)

    def test_access_token(self) -> None:
        """Test the access token is parsed correctly"""

        self.assertEqual(self.access_token, self.jwt.access)
        self.assertEqual(self.access_expiration, self.jwt.access_expiration)

    def test_refresh_token(self) -> None:
        """Test the refresh token is parsed correctly"""

        self.assertEqual(self.refresh_token, self.jwt.refresh)
        self.assertEqual(self.refresh_expiration, self.jwt.refresh_expiration)


class HS256Parsing(BaseTests, TestCase):
    """Test JWT token parsing using the HS256 algorithm."""

    algorithm = 'HS256'
