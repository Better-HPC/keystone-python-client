from unittest.mock import Mock, patch
from urllib.parse import urljoin

import httpx

from keystone_client.http import HTTPClient
from tests import API_HOST, API_PASSWORD, API_USER


@patch('httpx.Client.request')
class CommonHttpMethodTests:
    """Base class for HTTP method tests with common setup and assertions."""

    request_type: str
    method_name: str
    method_args: dict[str, str]

    _request_endpoint = "test/endpoint/"

    def setUp(self) -> None:
        """Set a client instance for each test case."""

        self.client = HTTPClient(API_HOST)
        self.method_to_test = getattr(self.client, self.method_name)

        # Setup mock objects
        self.mock_response = Mock()
        self.mock_response.raise_for_status = Mock()

    def assert_http_request_called(self) -> None:
        """Assert that the request was called with expected arguments."""

        self.mock_request.assert_called_with(
            method=self.request_type,
            url=urljoin(self.client.base_url, self._request_endpoint),
            headers=self.client._csrf_headers(),
            **self.method_args
        )
        self.mock_response.raise_for_status.assert_called_once()

    def test_unauthenticated_request(self, mock_request: Mock) -> None:
        """Test the HTTP method for a successful, unauthenticated request."""

        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        self.method_to_test(self._request_endpoint, **self.method_args)
        self.assert_http_request_called()

    def test_authenticated_request(self, mock_request: Mock) -> None:
        """Test the HTTP method for a successful, authenticated request."""

        self.client.login(API_USER, API_PASSWORD)
        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        self.method_to_test(self._request_endpoint, **self.method_args)
        self.assert_http_request_called()

    def test_http_error(self, mock_request: Mock) -> None:
        """Test the HTTP method for a failed request."""

        self.mock_response.raise_for_status.side_effect = httpx.HTTPError("Error")
        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        with self.assertRaises(httpx.HTTPError):
            self.method_to_test(self._request_endpoint, **self.method_args)

        self.assert_http_request_called()

    def test_connection_error(self, mock_request: Mock) -> None:
        """Test that a connection error is raised."""

        self.mock_request = mock_request
        self.mock_request.side_effect = httpx.ConnectionError("Connection error")

        with self.assertRaises(httpx.ConnectionError):
            self.method_to_test(self._request_endpoint, **self.method_args)
