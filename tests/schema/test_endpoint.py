"""Tests for the `Endpoint` class."""

from unittest import TestCase

from keystone_client.schema import Endpoint


class Resolve(TestCase):
    """Tests for the `resolve` method"""

    def test_trailing_slash(self) -> None:
        """Test endpoints are always resolved with a single trailing slash"""

        url = 'https://example.com/'
        expected_url = 'https://example.com/api/endpoint/'

        self.assertEqual(expected_url, Endpoint('api/endpoint').resolve(url))
        self.assertEqual(expected_url, Endpoint('api/endpoint/').resolve(url))
        self.assertEqual(expected_url, Endpoint('api/endpoint//').resolve(url))
        self.assertEqual(expected_url, Endpoint('api/endpoint///').resolve(url))
