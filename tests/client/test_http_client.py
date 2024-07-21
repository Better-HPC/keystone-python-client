"""Tests for the handling to the base API url."""

from unittest import TestCase

from keystone_client import HTTPClient


class Url(TestCase):
    """Tests for the `url` property"""

    def test_has_trailing_slash(self) -> None:
        """Test the base URL is returned with a single trailing slash"""

        url_no_slash = 'http://test.domain.com'

        # Test for various numbers of trailing slashes
        self.assertEqual(url_no_slash + '/', HTTPClient(url_no_slash).url)
        self.assertEqual(url_no_slash + '/', HTTPClient(url_no_slash + '/').url)
        self.assertEqual(url_no_slash + '/', HTTPClient(url_no_slash + '////').url)


class ResolveEndpoint(TestCase):
    """Tests for the `resolve_endpoint` method"""

    def test_trailing_slash(self) -> None:
        """Test rendered endpoints are always resolved with a single trailing slash"""

        client = HTTPClient(url='https://example.com')
        expected_url = 'https://example.com/api/endpoint/'
        self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint'))
        self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint/'))
        self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint//'))
        self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint//'))

    def test_leading_slash(self) -> None:
        """Test rendered endpoints resolved correctly regardless of leading slashes"""

        client = HTTPClient(url='https://example.com')
        expected_url = 'https://example.com/api/endpoint/'
        self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint/'))
        self.assertEqual(expected_url, client.resolve_endpoint('/api/endpoint/'))
        self.assertEqual(expected_url, client.resolve_endpoint('//api/endpoint/'))
        self.assertEqual(expected_url, client.resolve_endpoint('///api/endpoint/'))
