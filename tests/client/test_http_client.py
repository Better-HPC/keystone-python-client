"""Tests for the `HTTPClient` class"""

from unittest import TestCase
from unittest.mock import Mock, patch
from urllib.parse import urljoin

import requests

from keystone_client.client import HTTPClient
from .. import API_HOST, API_PASSWORD, API_USER


class Url(TestCase):
    """Tests for the `url` property"""

    def test_trailing_slash_removed(self) -> None:
        """Test extra trailing slashes are removed from URLs provided at init"""

        base_url = 'https://test.domain.com'
        expected_url = base_url + '/'

        # Test for various numbers of trailing slashes provided at init
        self.assertEqual(expected_url, HTTPClient(base_url).url)
        self.assertEqual(expected_url, HTTPClient(base_url + '/').url)
        self.assertEqual(expected_url, HTTPClient(base_url + '////').url)


@patch('requests.request')
class BaseHttpMethodTests:
    """Base class for HTTP method tests with common setup and assertions"""

    client_method: str
    request_type: str
    request_params: dict[str, str]
    endpoint_str = "test/endpoint"

    def setUp(self) -> None:
        """Set up variables and a client instance for each test case"""

        self.client = HTTPClient(API_HOST)
        self.method_to_test = getattr(self.client, self.client_method)

        # Setup mock objects
        self.mock_response = Mock()
        self.mock_response.raise_for_status = Mock()

    def assert_http_request_called(self) -> None:
        """Assert that the request was called with expected arguments"""

        self.mock_request.assert_called_once_with(
            self.request_type,
            urljoin(self.client.url, self.endpoint_str),
            headers=self.client._auth.get_auth_headers(),
            **self.request_params
        )
        self.mock_response.raise_for_status.assert_called_once()

    def test_unauthenticated_request(self, mock_request: Mock) -> None:
        """Test the HTTP method for a successful, unauthenticated request"""

        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        self.method_to_test(self.endpoint_str, **self.request_params)
        self.assert_http_request_called()

    def test_authenticated_request(self, mock_request: Mock) -> None:
        """Test the HTTP method for a successful, authenticated request"""

        self.client.login(API_USER, API_PASSWORD)
        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        self.method_to_test(self.endpoint_str, **self.request_params)
        self.assert_http_request_called()

    def test_http_error(self, mock_request: Mock) -> None:
        """Test the HTTP method for a failed request"""

        self.mock_response.raise_for_status.side_effect = requests.HTTPError("Error")
        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        with self.assertRaises(requests.HTTPError):
            self.method_to_test(self.endpoint_str, **self.request_params)

        self.assert_http_request_called()


class HttpGetTest(BaseHttpMethodTests, TestCase):
    """Tests for the `http_get` method"""

    request_type = 'get'
    client_method = 'http_get'
    request_params = {'params': {"key": "value"}, 'timeout': 10}


class HttpPostTest(BaseHttpMethodTests, TestCase):
    """Tests for the `http_post` method"""

    request_type = 'post'
    client_method = 'http_post'
    request_params = {'data': {"key": "value"}, 'timeout': 10}


class HttpPatchTest(BaseHttpMethodTests, TestCase):
    """Tests for the `http_patch` method"""

    request_type = 'patch'
    client_method = 'http_patch'
    request_params = {'data': {"key": "value"}, 'timeout': 10}


class HttpPutTest(BaseHttpMethodTests, TestCase):
    """Tests for the `http_put` method"""

    request_type = 'put'
    client_method = 'http_put'
    request_params = {'data': {"key": "value"}, 'timeout': 10}


class HttpDeleteTest(BaseHttpMethodTests, TestCase):
    """Tests for the `http_delete` method"""

    request_type = 'delete'
    client_method = 'http_delete'
    request_params = {'timeout': 10}
