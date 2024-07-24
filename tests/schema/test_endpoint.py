"""Tests for the `Endpoint` class."""

from unittest import TestCase

from keystone_client.schema import Endpoint


class JoinUrl(TestCase):
    """Tests for the `join_url` method"""

    def test_with_trailing_slash(self) -> None:
        """Test join_url with a base URL that has a trailing slash"""

        endpoint = Endpoint("authentication/new")
        base_url = "https://api.example.com/"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url))

    def test_without_trailing_slash(self) -> None:
        """Test join_url with a base URL that does not have a trailing slash"""

        endpoint = Endpoint("authentication/new")
        base_url = "https://api.example.com"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url))

    def test_with_endpoint_trailing_slash(self) -> None:
        """Test join_url with an endpoint that has a trailing slash"""

        endpoint = Endpoint("authentication/new/")
        base_url = "https://api.example.com"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url))

    def test_without_endpoint_trailing_slash(self) -> None:
        """Test join_url with an endpoint that does not have a trailing slash"""

        endpoint = Endpoint("authentication/new")
        base_url = "https://api.example.com"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url))

    def test_with_complete_url_as_endpoint(self) -> None:
        """Test join_url when the endpoint is a complete URL"""

        endpoint = Endpoint("https://anotherapi.com/authentication/new")
        base_url = "https://api.example.com"
        expected_result = "https://anotherapi.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url))
