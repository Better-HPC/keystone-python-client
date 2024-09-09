"""Test the sending of HTTP requests."""

from unittest import TestCase
from unittest.mock import Mock, patch
from urllib.parse import urljoin

import requests
from requests import HTTPError

from keystone_client.client import HTTPClient
from tests import API_HOST, API_PASSWORD, API_USER


class Url(TestCase):
    """Tests for the `url` property."""

    def test_trailing_slash_removed(self) -> None:
        """Test extra trailing slashes are removed from URLs provided at init."""

        base_url = 'https://test.domain.com'
        expected_url = base_url + '/'

        # Test for various numbers of trailing slashes provided at init
        self.assertEqual(expected_url, HTTPClient(base_url).url)
        self.assertEqual(expected_url, HTTPClient(base_url + '/').url)
        self.assertEqual(expected_url, HTTPClient(base_url + '////').url)


class Login(TestCase):
    """Test session authentication via the `login` method."""

    def test_with_correct_credentials(self) -> None:
        """Test users are successfully logged in/out when providing correct credentials."""

        client = HTTPClient(API_HOST)
        self.assertFalse(client.is_authenticated())

        client.login(API_USER, API_PASSWORD)
        self.assertTrue(client.is_authenticated())

    def test_with_incorrect_credentials(self) -> None:
        """Test an error is raised when authenticating with invalid credentials."""

        client = HTTPClient(API_HOST)
        with self.assertRaises(HTTPError) as error:
            client.login('foo', 'bar')
            self.assertEqual(401, error.response.status_code)

    def test_user_already_logged_in(self) -> None:
        """Test the method succeeds when re-logging in a successful user"""

        client = HTTPClient(API_HOST)
        self.assertFalse(client.is_authenticated())

        client.login(API_USER, API_PASSWORD)
        client.login(API_USER, API_PASSWORD)
        self.assertTrue(client.is_authenticated())

    @patch('requests.post')
    def test_errors_are_forwarded(self, mock_post: Mock) -> None:
        """Test errors are forwarded to the user during login."""

        mock_post.side_effect = requests.ConnectionError()

        client = HTTPClient(API_HOST)
        with self.assertRaises(requests.ConnectionError):
            client.login(API_USER, API_PASSWORD)


class Logout(TestCase):
    """Test session invalidation via the `logout` method."""

    def setUp(self) -> None:
        """Authenticate a new `AuthenticationManager` instance."""

        self.client = HTTPClient(API_HOST)
        self.client.login(API_USER, API_PASSWORD)

    def test_user_is_logged_out(self) -> None:
        """Test the credentials are cleared and the user is logged out."""

        self.assertTrue(self.client.is_authenticated())
        self.client.logout()
        self.assertFalse(self.client.is_authenticated())

    def test_user_already_logged_out(self) -> None:
        """Test the `logout` method exits silents when the user is not authenticated"""

        client = HTTPClient(API_HOST)
        self.assertFalse(client.is_authenticated())
        client.logout()
        self.assertFalse(client.is_authenticated())

    @patch('requests.post')
    def test_errors_are_forwarded(self, mock_post: Mock) -> None:
        """Test errors are forwarded to the user during logout."""

        mock_post.side_effect = requests.ConnectionError()

        with self.assertRaises(requests.ConnectionError):
            self.client.login(API_USER, API_PASSWORD)


@patch('requests.request')
class BaseHttpMethodTests:
    """Base class for HTTP method tests with common setup and assertions."""

    client_method: str
    request_type: str
    request_params: dict[str, str]
    endpoint_str = "test/endpoint"

    def setUp(self) -> None:
        """Set a client instance for each test case."""

        self.client = HTTPClient(API_HOST)
        self.method_to_test = getattr(self.client, self.client_method)

        # Setup mock objects
        self.mock_response = Mock()
        self.mock_response.raise_for_status = Mock()

    def assert_http_request_called(self) -> None:
        """Assert that the request was called with expected arguments."""

        self.mock_request.assert_called_once_with(
            self.request_type,
            urljoin(self.client.url, self.endpoint_str),
            headers=self.client._auth.get_auth_headers(),
            **self.request_params
        )
        self.mock_response.raise_for_status.assert_called_once()

    def test_unauthenticated_request(self, mock_request: Mock) -> None:
        """Test the HTTP method for a successful, unauthenticated request."""

        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        self.method_to_test(self.endpoint_str, **self.request_params)
        self.assert_http_request_called()

    def test_authenticated_request(self, mock_request: Mock) -> None:
        """Test the HTTP method for a successful, authenticated request."""

        self.client.login(API_USER, API_PASSWORD)
        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        self.method_to_test(self.endpoint_str, **self.request_params)
        self.assert_http_request_called()

    def test_http_error(self, mock_request: Mock) -> None:
        """Test the HTTP method for a failed request."""

        self.mock_response.raise_for_status.side_effect = requests.HTTPError("Error")
        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        with self.assertRaises(requests.HTTPError):
            self.method_to_test(self.endpoint_str, **self.request_params)

        self.assert_http_request_called()

    def test_connection_error(self, mock_request: Mock) -> None:
        """Test that a connection error is raised."""

        self.mock_request = mock_request
        self.mock_request.side_effect = requests.ConnectionError("Connection error")

        with self.assertRaises(requests.ConnectionError):
            self.method_to_test(self.endpoint_str, **self.request_params)


class HttpGet(BaseHttpMethodTests, TestCase):
    """Tests for the `http_get` method."""

    request_type = 'get'
    client_method = 'http_get'
    request_params = {'params': {"key": "value"}, 'timeout': 10}


class HttpPost(BaseHttpMethodTests, TestCase):
    """Tests for the `http_post` method."""

    request_type = 'post'
    client_method = 'http_post'
    request_params = {'data': {"key": "value"}, 'timeout': 10}


class HttpPatch(BaseHttpMethodTests, TestCase):
    """Tests for the `http_patch` method."""

    request_type = 'patch'
    client_method = 'http_patch'
    request_params = {'data': {"key": "value"}, 'timeout': 10}


class HttpPut(BaseHttpMethodTests, TestCase):
    """Tests for the `http_put` method."""

    request_type = 'put'
    client_method = 'http_put'
    request_params = {'data': {"key": "value"}, 'timeout': 10}


class HttpDelete(BaseHttpMethodTests, TestCase):
    """Tests for the `http_delete` method."""

    request_type = 'delete'
    client_method = 'http_delete'
    request_params = {'timeout': 10}
