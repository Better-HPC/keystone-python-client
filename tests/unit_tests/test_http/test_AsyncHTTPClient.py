"""Unit tests for the `AsyncHTTPClient` method."""

import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import urljoin

import httpx

from keystone_client.http import AsyncHTTPClient
from tests.unit_tests import utils


@patch("httpx.AsyncClient")
class CloseMethodAsync(IsolatedAsyncioTestCase):
    """Test the termination of open connections."""

    async def test_close_on_function_call(self, mock_httpx_class: MagicMock) -> None:
        """Verify any open sessions are closed when calling the `close` method."""

        mock_httpx_class.return_value.aclose = AsyncMock()

        client = AsyncHTTPClient(base_url="https://example.com")
        await client.close()

        mock_httpx_class.return_value.aclose.assert_called_once()

    async def test_close_on_exit(self, mock_httpx_class: MagicMock) -> None:
        """Verify any open sessions are closed when exiting a context manager."""

        mock_httpx_class.return_value.aclose = AsyncMock()

        async with AsyncHTTPClient(base_url="https://example.com") as client:
            pass

        mock_httpx_class.return_value.aclose.assert_called_once()


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

    async def test_logs_request(self) -> None:
        """Verify that sending a request produces a properly populated log record."""

        expected_method = 'get'
        expected_endpoint = '/v1/resource'
        expected_url = self.client.normalize_url(urljoin(self.base_url, 'v1/resource'))

        with self.assertLogs("kclient", level="INFO") as log_watcher:
            await self.client.send_request(expected_method, expected_endpoint)

        self.assertEqual(len(log_watcher.records), 1)

        record = log_watcher.records[0]
        self.assertEqual(logging.INFO, record.levelno)
        self.assertEqual(self.client.cid, record.cid)
        self.assertEqual(self.client.base_url, record.baseurl)
        self.assertEqual(expected_method, record.method)
        self.assertEqual(expected_endpoint, record.endpoint)
        self.assertEqual(expected_url, record.url)
