"""Unit tests for the `HTTPClient` class."""

from unittest import TestCase
from unittest.mock import MagicMock, patch

import httpx

from keystone_client.http import HTTPClient
from tests.unit_tests import utils


@patch("httpx.Client")
class CloseMethod(TestCase):
    """Test the termination of open connections."""

    def test_close_on_function_call(self, mock_httpx_class: MagicMock) -> None:
        """Verify any open sessions are closed when calling the `close` method."""

        client = HTTPClient(base_url="https://example.com")
        client.close()

        mock_httpx_class.return_value.close.assert_called_once()

    def test_close_on_exit(self, mock_httpx_class: MagicMock) -> None:
        """Verify any open sessions are closed when exiting a context manager."""

        with  HTTPClient(base_url="https://example.com") as client:
            pass

        mock_httpx_class.return_value.close.assert_called_once()


class SendRequestMethod(TestCase):
    """Test HTTP requests issued by the `send_requests` method."""

    def setUp(self) -> None:
        """Create a new client instance using a dummy HTTP request handler."""

        self.base_url = 'https://test.api'
        self.transport = httpx.MockTransport(utils.mock_request_handler)
        self.client = HTTPClient(self.base_url, transport=self.transport)

    def test_uses_normalized_url(self) -> None:
        """Verify requests are sent to the normalized application URL."""

        response = self.client.send_request('get', 'v1/resource', params={'q': '1'})
        request_details = response.json()

        self.assertEqual(request_details['url'], f'{self.base_url}/v1/resource/?q=1')
        self.assertEqual(request_details['method'], 'GET')

    def test_includes_application_headers(self) -> None:
        """Verify requests include application headers."""

        response = self.client.send_request('get', 'v1/resource')
        request_details = response.json()

        self.assertIn(HTTPClient.CID_HEADER.lower(), request_details['headers'])
