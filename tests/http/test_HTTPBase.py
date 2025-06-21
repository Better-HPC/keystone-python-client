"""Unit tests for the `HTTPBase` class."""

from unittest import TestCase
from unittest.mock import MagicMock

from keystone_client.http import HTTPBase


class NormalizeUrlMethod(TestCase):
    """Test the normalization of URL paths."""

    def test_trailing_slash_enforced(self) -> None:
        """Verify the URL is returned with a single trailing slash."""

        base_url = 'https://test.domain.com'
        expected_url = base_url + '/'

        # Test for various numbers of trailing slashes provided at init
        self.assertEqual(expected_url, HTTPBase.normalize_url(base_url))
        self.assertEqual(expected_url, HTTPBase.normalize_url(base_url + '/'))
        self.assertEqual(expected_url, HTTPBase.normalize_url(base_url + '////'))

    def test_no_intermediate_slashes(self) -> None:
        """Verify duplicate slashes are removed from the URL path."""

        base_url = 'https://test.domain.com///path/'
        expected_url = 'https://test.domain.com/path/'
        self.assertEqual(expected_url, HTTPBase.normalize_url(base_url))


class GetApplicationHeadersMethod(TestCase):
    """Test the application headers returned for a session."""

    def setUp(self) -> None:
        """Create a HTTPBase instance with a mocked client."""

        self.base_url = 'https://test.domain.com/'
        self.http_base = HTTPBase(self.base_url)

        self.http_base._client = MagicMock()
        self.http_base._client.cookies = {}

    def test_cid_header_always_included(self) -> None:
        """Verify the `X-KEYSTONE-CID` header is included."""

        headers = self.http_base.get_application_headers()

        self.assertIn('X-KEYSTONE-CID', headers)
        self.assertEqual(headers['X-KEYSTONE-CID'], self.http_base._cid)

    def test_csrf_token_included_if_present(self) -> None:
        """Verify the CSRF token header is included if available."""

        csrf_token = 'dummy-token'
        self.http_base._client.cookies = {HTTPBase._CSRF_COOKIE: csrf_token}

        headers = self.http_base.get_application_headers()

        self.assertIn('X-CSRFToken', headers)
        self.assertEqual(csrf_token, headers['X-CSRFToken'])

    def test_csrf_token_not_included_if_absent(self) -> None:
        """Verify the CSRF token header is omitted if not available."""

        self.http_base._client.cookies = {}
        headers = self.http_base.get_application_headers()
        self.assertNotIn('X-CSRFToken', headers)
