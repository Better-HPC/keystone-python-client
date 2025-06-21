"""Unit tests for the `HTTPClient` class."""

from unittest import TestCase

import httpx

from keystone_client.http import HTTPClient
from tests.unittests import utils


class SendRequestMethod(TestCase):
    """Test the HTTPClient.send_request method."""

    def setUp(self) -> None:
        """Create a new client instance using a dummy HTTP request handler."""

        self.base_url = 'https://test.api'
        self.transport = httpx.MockTransport(utils.test_request_handler)
        self.client = HTTPClient(self.base_url, transport=self.transport)

    def test_normalized_url(self) -> None:
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
