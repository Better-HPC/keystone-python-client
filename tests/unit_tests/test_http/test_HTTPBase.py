"""Unit tests for the `HTTPBase` class."""

import uuid
from unittest import TestCase
from unittest.mock import MagicMock

from keystone_client.http import HTTPBase


class DummyHTTPBase(HTTPBase):
    """Concrete subclass of HTTPBase for testing."""

    def _client_factory(self, **kwargs) -> MagicMock:
        """Create a mock object as a stand in for an HTTP client."""

        return MagicMock(cookies={})


class BaseUrlProperty(TestCase):
    """Test the `base_url` property returns the correct value."""

    def test_returns_normalized_url(self) -> None:
        """Verify the `base_url` property returns the normalized URL."""

        http_base = DummyHTTPBase('https://example.com//')
        expected_url = 'https://example.com/'
        self.assertEqual(expected_url, http_base.base_url)


class CidProperty(TestCase):
    """Test the `cid` property returns a UUID value."""

    def test_returns_valid_uuid(self) -> None:
        """Verify the `cid` property returns a valid UUID."""

        http_base = DummyHTTPBase('https://example.com/')

        try:
            uuid.UUID(http_base.cid, version=4)

        except ValueError:
            self.fail(f"cid '{http_base.cid}' is not a valid UUID4")


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
    """Test fetching a session's application headers."""

    def setUp(self) -> None:
        """Create a HTTPBase instance with a mocked client."""

        self.base_url = 'https://test.domain.com/'
        self.http_base = DummyHTTPBase(self.base_url)

    def test_cid_header_included(self) -> None:
        """Verify the `X-KEYSTONE-CID` header is included."""

        headers = self.http_base.get_application_headers()

        self.assertIn('X-KEYSTONE-CID', headers)
        self.assertEqual(headers['X-KEYSTONE-CID'], self.http_base._cid)

    def test_csrf_token_included_if_present(self) -> None:
        """Verify the CSRF token header is included if available."""

        csrf_token = 'dummy-token'
        self.http_base._client.cookies = {HTTPBase.CSRF_COOKIE: csrf_token}

        headers = self.http_base.get_application_headers()

        self.assertIn('X-CSRFToken', headers)
        self.assertEqual(csrf_token, headers['X-CSRFToken'])

    def test_csrf_token_not_included_if_absent(self) -> None:
        """Verify the CSRF token header is omitted if not available."""

        self.http_base._client.cookies = {}
        headers = self.http_base.get_application_headers()
        self.assertNotIn('X-CSRFToken', headers)

    def test_header_overrides_add_new_header(self) -> None:
        """Verify provided values are included in the returned headers."""

        custom_value = 'test-value'
        overrides = {'X-Test-Header': custom_value}
        headers = self.http_base.get_application_headers(overrides)

        self.assertIn('X-Test-Header', headers)
        self.assertEqual(custom_value, headers['X-Test-Header'])

    def test_header_overrides_replace_existing_header(self) -> None:
        """Verify provided values overwrite application specific headers."""

        custom_cid = 'custom-cid-value'
        overrides = {HTTPBase.CID_HEADER: custom_cid}
        headers = self.http_base.get_application_headers(overrides)

        self.assertEqual(custom_cid, headers[HTTPBase.CID_HEADER])
