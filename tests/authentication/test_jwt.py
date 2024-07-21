"""Tests for the `JWT` class."""

from datetime import datetime, timedelta
from unittest import TestCase

import jwt

from keystone_client.authentication import JWT


class BaseTests:
    """Base class containing reusable tests"""

    algorithm: str

    def test_parsing(self) -> None:
        """Test the parsing of JWT data"""

        # Build a JWT
        access_expiration = datetime.now() + timedelta(hours=1)
        access_token = jwt.encode({'exp': access_expiration.timestamp()}, 'secret', algorithm=self.algorithm)

        refresh_expiration = datetime.now() + timedelta(days=1)
        refresh_token = jwt.encode({'exp': refresh_expiration.timestamp()}, 'secret', algorithm=self.algorithm)

        token = JWT(access_token, refresh_token, self.algorithm)

        # Check parsed values against original inputs
        self.assertEqual(access_token, token.access)
        self.assertEqual(access_expiration, token.access_expiration)

        self.assertEqual(refresh_token, token.refresh)
        self.assertEqual(refresh_expiration, token.refresh_expiration)


class HS256Parsing(BaseTests, TestCase):
    """Test JWT token parsing using the HS256 algorithm."""

    algorithm = 'HS256'
