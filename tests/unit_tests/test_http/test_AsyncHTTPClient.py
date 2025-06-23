"""Unit tests for the `AsyncHTTPClient` method."""

from unittest import IsolatedAsyncioTestCase

import httpx

from keystone_client.http import AsyncHTTPClient
from tests.unit_tests import utils


class SendRequestMethodAsync(IsolatedAsyncioTestCase):
    """Test HTTP requests issued by the `send_requests` method."""

    async def asyncSetUp(self) -> None:
        """Create a new async client instance using a dummy HTTP request handler."""

        self.base_url = 'https://test.api'
        self.transport = httpx.MockTransport(utils.mock_request_handler)
        self.client = AsyncHTTPClient(self.base_url, transport=self.transport)

    async def test_uses_normalized_url(self) -> None:
        """Verify requests are sent to the normalized application URL."""

        response = await self.client.send_request('get', 'v1/resource', params={'q': '1'})
        request_details = response.json()

        self.assertEqual(request_details['url'], f'{self.base_url}/v1/resource/?q=1')
        self.assertEqual(request_details['method'], 'GET')

    async def test_includes_application_headers(self) -> None:
        """Verify requests include application headers."""

        response = await self.client.send_request('get', 'v1/resource')
        request_details = response.json()

        self.assertIn(AsyncHTTPClient.CID_HEADER.lower(), request_details['headers'])
