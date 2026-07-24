"""Unit tests for the `HTTPClient` class."""

import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from urllib.parse import urljoin

import httpx

from keystone_client.http import HTTPClient
from tests.unit_tests import utils


class CloseAtExit(TestCase):
    """Tests the registration of `close` with `atexit`.

    Verifies the client's cleanup logic is registered to run
    automatically when the interpreter exits.
    """

    @patch('atexit.register')
    def test_close_registered_with_atexit(self, mock_atexit_register: MagicMock) -> None:
        """Verify the `close` method is registered with `atexit` on initialization."""

        client = HTTPClient(base_url="https://example.com")
        mock_atexit_register.assert_any_call(client.close)


@patch("httpx.Client")
class CloseMethod(TestCase):
    """Tests the `close` method.

    Verifies any open connections are terminated when the method is called
    directly, and when the client is exited via its context manager.
    """

    def test_close_on_function_call(self, mock_httpx_class: MagicMock) -> None:
        """Verify any open sessions are closed when calling the `close` method."""

        client = HTTPClient(base_url="https://example.com")
        client.close()

        mock_httpx_class.return_value.close.assert_called_once()

    def test_close_on_exit(self, mock_httpx_class: MagicMock) -> None:
        """Verify any open sessions are closed when exiting a context manager."""

        with HTTPClient(base_url="https://example.com") as client:
            pass

        mock_httpx_class.return_value.close.assert_called_once()

    def test_close_when_already_closed(self, mock_httpx_class: MagicMock) -> None:
        """Verify calling `close` on an already closed client is a no-op."""

        client = HTTPClient(base_url="https://example.com")
        client.close()
        client.close()

        mock_httpx_class.return_value.close.assert_called_once()


class SendRequestMethod(TestCase):
    """Tests the `send_request` method.

    Verifies outgoing requests are addressed to the correctly normalized
    URL, include the expected application headers, and produce a log
    record describing the request.
    """

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

    def test_logs_request(self) -> None:
        """Verify that sending a request produces a properly populated log record."""

        expected_method = 'get'
        expected_endpoint = '/v1/resource'
        expected_url = self.client.normalize_url(urljoin(self.base_url, 'v1/resource'))

        with self.assertLogs("kclient", level="INFO") as log_watcher:
            self.client.send_request(expected_method, expected_endpoint)

        self.assertEqual(len(log_watcher.records), 1)

        record = log_watcher.records[0]
        self.assertEqual(logging.INFO, record.levelno)
        self.assertEqual(self.client.cid, record.cid)
        self.assertEqual(self.client.base_url, record.baseurl)
        self.assertEqual(expected_method, record.method)
        self.assertEqual(expected_endpoint, record.endpoint)
        self.assertEqual(expected_url, record.url)


class HttpMethodShortcuts(TestCase):
    """Tests the `http_get`, `http_post`, `http_patch`, `http_put`, and `http_delete` methods.

    Verifies each shortcut method issues a request using its corresponding
    HTTP verb against the target endpoint.
    """

    def setUp(self) -> None:
        """Create a new client instance using a dummy HTTP request handler."""

        self.base_url = 'https://test.api'
        self.transport = httpx.MockTransport(utils.mock_request_handler)
        self.client = HTTPClient(self.base_url, transport=self.transport)

    def test_sends_correct_http_verb(self) -> None:
        """Verify each shortcut method issues a request with the matching HTTP verb."""

        shortcuts = (
            (self.client.http_get, 'GET'),
            (self.client.http_post, 'POST'),
            (self.client.http_patch, 'PATCH'),
            (self.client.http_put, 'PUT'),
            (self.client.http_delete, 'DELETE'),
        )

        for shortcut, expected_verb in shortcuts:
            with self.subTest(verb=expected_verb):
                response = shortcut('v1/resource')
                request_details = response.json()
                self.assertEqual(expected_verb, request_details['method'])
