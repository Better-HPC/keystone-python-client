"""Unit tests for the `HTTPBase` class."""

from unittest import TestCase

from keystone_client.http import HTTPBase


class BaseUrlProperty(TestCase):
    """Tests for the `base_url` property."""

    def test_trailing_slash_enforced(self) -> None:
        """Verify the URL is returned with a single trailing slash."""

        base_url = 'https://test.domain.com'
        expected_url = base_url + '/'

        # Test for various numbers of trailing slashes provided at init
        self.assertEqual(expected_url, HTTPBase(base_url).base_url)
        self.assertEqual(expected_url, HTTPBase(base_url + '/').base_url)
        self.assertEqual(expected_url, HTTPBase(base_url + '////').base_url)

    def test_no_intermediate_slashes(self) -> None:
        """Verify duplicate slashes are removed from the URL path."""

        base_url = 'https://test.domain.com///path/'
        expected_url = 'https://test.domain.com/path/'
        self.assertEqual(expected_url, HTTPBase(base_url).base_url)
