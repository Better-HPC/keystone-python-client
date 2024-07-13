"""Tests for the handling to the base API url."""

from unittest import TestCase

from keystone_client import KeystoneClient


class TestUrl(TestCase):
    """Tests for the `url` property"""

    def test_trailing_slash_removed(self):
        """Test trailing slashes are removed from URLs provided at init"""

        url = 'http://test.domain.com'
        self.assertEqual(url, KeystoneClient(url + '/').url)
        self.assertEqual(url, KeystoneClient(url + '////').url)
