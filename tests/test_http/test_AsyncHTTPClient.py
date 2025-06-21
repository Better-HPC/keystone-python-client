"""Unit tests for the `AsyncHTTPClient` method."""

from unittest import IsolatedAsyncioTestCase

import httpx

from keystone_client.http import AsyncHTTPClient
from tests import utils


class SendRequestMethodAsync(IsolatedAsyncioTestCase):
    """Test the AsyncHTTPClient.send_request method."""

    async def asyncSetUp(self) -> None:
        """Create a new async client instance using a dummy HTTP request handler."""

        self.base_url = 'https://test.api'
        self.transport = httpx.MockTransport(utils.test_request_handler)
        self.client = AsyncHTTPClient(self.base_url, transport=self.transport)

    async def test_normalized_url(self) -> None:
        """Verify requests are sent to the normalized application URL."""

        response = await self.client.send_request('get', 'v1/resource', params={'q': '1'})
        data = response.json()

        self.assertEqual(data['url'], f'{self.base_url}/v1/resource/?q=1')
        self.assertEqual(data['method'], 'GET')

    async def test_includes_application_headers(self) -> None:
        """Verify requests include application headers."""

        response = await self.client.send_request('get', 'v1/resource')
        data = response.json()

        self.assertIn(AsyncHTTPClient.CID_HEADER.lower(), data['headers'])
