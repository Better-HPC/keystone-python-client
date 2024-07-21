"""Tests for the handling to the base API url."""

from unittest import TestCase

from keystone_client.client import HTTPClient


class Url(TestCase):
    """Tests for the `url` property"""

    def test_has_trailing_slash(self) -> None:
        """Test the base URL is returned with a single trailing slash"""

        url_no_slash = 'http://test.domain.com'

        # Test for various numbers of trailing slashes
        self.assertEqual(url_no_slash + '/', HTTPClient(url_no_slash).url)
        self.assertEqual(url_no_slash + '/', HTTPClient(url_no_slash + '/').url)
        self.assertEqual(url_no_slash + '/', HTTPClient(url_no_slash + '////').url)

