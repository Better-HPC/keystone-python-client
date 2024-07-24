"""Tests for the `HTTPClient` class."""

from unittest import TestCase

from keystone_client.client import HTTPClient


class TestUrl(TestCase):
    """Tests for the `url` property"""

    def test_trailing_slash_removed(self):
        """Test extra trailing slashes are removed from URLs provided at init"""

        base_url = 'https://test.domain.com'
        expected_url = base_url + '/'

        # Test for various numbers of trailing slashes provided at init
        self.assertEqual(expected_url, HTTPClient(base_url).url)
        self.assertEqual(expected_url, HTTPClient(base_url + '/').url)
        self.assertEqual(expected_url, HTTPClient(base_url + '////').url)
