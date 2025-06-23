"""Test the formatting of API endpoints and URLs."""

from unittest import TestCase

from keystone_client.schema import Endpoint


class JoinUrlMethod(TestCase):
    """Test the joining of URL parts via the `join_url` method."""

    def test_with_trailing_slash(self) -> None:
        """Verify a base URL with a trailing slash is joined correctly."""

        endpoint = Endpoint("authentication/new")
        base_url = "https://api.example.com/"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url))

    def test_without_trailing_slash(self) -> None:
        """Verify a base URL with a trailing slash is joined correctly."""

        endpoint = Endpoint("authentication/new")
        base_url = "https://api.example.com"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url))

    def test_with_endpoint_trailing_slash(self) -> None:
        """Verify an endpoint with a trailing slash is joined correctly."""

        endpoint = Endpoint("authentication/new/")
        base_url = "https://api.example.com"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url))

    def test_without_endpoint_trailing_slash(self) -> None:
        """Verify an endpoint without a trailing slash is joined correctly."""

        endpoint = Endpoint("authentication/new")
        base_url = "https://api.example.com"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url))

    def test_with_append_trailing_slash(self) -> None:
        """Verify an append path with a trailing slash is joined correctly."""

        endpoint = Endpoint("authentication")
        base_url = "https://api.example.com"
        append_path = "new/"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url, append_path))

    def test_without_append_trailing_slash(self) -> None:
        """Verify an append path without a trailing slash is joined correctly."""

        endpoint = Endpoint("authentication")
        base_url = "https://api.example.com"
        append_path = "new"
        expected_result = "https://api.example.com/authentication/new/"
        self.assertEqual(expected_result, endpoint.join_url(base_url, append_path))

    def test_with_mixed_trailing_slash_in_append(self) -> None:
        """Verify mixed trailing slashes in append paths are handled correctly."""

        endpoint = Endpoint("authentication")
        base_url = "https://api.example.com"
        append_path1 = "new/"
        append_path2 = "extra"
        expected_result = "https://api.example.com/authentication/new/extra/"
        self.assertEqual(expected_result, endpoint.join_url(base_url, append_path1, append_path2))

    def test_int_append_argument(self) -> None:
        """Verify an integer append argument is joined correctly."""

        endpoint = Endpoint("authentication")
        base_url = "https://api.example.com"
        append_path = 123
        expected_result = "https://api.example.com/authentication/123/"
        self.assertEqual(expected_result, endpoint.join_url(base_url, str(append_path)))

    def test_none_append_argument(self) -> None:
        """Verify a `None` append argument is ignored in joining."""

        endpoint = Endpoint("authentication")
        base_url = "https://api.example.com"
        append_path = None
        expected_result = "https://api.example.com/authentication/"
        self.assertEqual(expected_result, endpoint.join_url(base_url, append_path))
