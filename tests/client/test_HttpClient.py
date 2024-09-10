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

    def test_trailing_slash_enforced(self) -> None:
        """Test the URL is returned with a single trailing slash."""

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
            self.assertEqual(401, error.exception.response.status_code)

    def test_user_already_logged_in(self) -> None:
        """Test the method succeeds when re-logging in a successful user"""

        client = HTTPClient(API_HOST)
        self.assertFalse(client.is_authenticated())

        client.login(API_USER, API_PASSWORD)
        client.login(API_USER, API_PASSWORD)
        self.assertTrue(client.is_authenticated())

    @patch('requests.Session.request')
    def test_errors_are_forwarded(self, mock_request: Mock) -> None:
        """Test errors are forwarded to the user during login."""

        mock_request.side_effect = requests.ConnectionError()

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

    @patch('requests.Session.request')
    def test_errors_are_forwarded(self, mock_request: Mock) -> None:
        """Test errors are forwarded to the user during logout."""

        mock_request.side_effect = requests.ConnectionError()

        with self.assertRaises(requests.ConnectionError):
            self.client.login(API_USER, API_PASSWORD)


@patch('requests.Session.request')
class BaseHttpMethodTests:
    """Base class for HTTP method tests with common setup and assertions."""

    client_method_name: str
    client_method_args: dict[str, str]
    request_type: str
    request_endpoint = "test/endpoint"

    def setUp(self) -> None:
        """Set a client instance for each test case."""

        self.client = HTTPClient(API_HOST)
        self.method_to_test = getattr(self.client, self.client_method_name)

        # Setup mock objects
        self.mock_response = Mock()
        self.mock_response.raise_for_status = Mock()

    def assert_http_request_called(self) -> None:
        """Assert that the request was called with expected arguments."""

        self.mock_request.assert_called_with(
            method=self.request_type,
            url=urljoin(self.client.url, self.request_endpoint),
            headers=self.client._csrf_headers(),
            **self.client_method_args
        )
        self.mock_response.raise_for_status.assert_called_once()

    def test_unauthenticated_request(self, mock_request: Mock) -> None:
        """Test the HTTP method for a successful, unauthenticated request."""

        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        self.method_to_test(self.request_endpoint, **self.client_method_args)
        self.assert_http_request_called()

    def test_authenticated_request(self, mock_request: Mock) -> None:
        """Test the HTTP method for a successful, authenticated request."""

        self.client.login(API_USER, API_PASSWORD)
        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        self.method_to_test(self.request_endpoint, **self.client_method_args)
        self.assert_http_request_called()

    def test_http_error(self, mock_request: Mock) -> None:
        """Test the HTTP method for a failed request."""

        self.mock_response.raise_for_status.side_effect = requests.HTTPError("Error")
        self.mock_request = mock_request
        self.mock_request.return_value = self.mock_response

        with self.assertRaises(requests.HTTPError):
            self.method_to_test(self.request_endpoint, **self.client_method_args)

        self.assert_http_request_called()

    def test_connection_error(self, mock_request: Mock) -> None:
        """Test that a connection error is raised."""

        self.mock_request = mock_request
        self.mock_request.side_effect = requests.ConnectionError("Connection error")

        with self.assertRaises(requests.ConnectionError):
            self.method_to_test(self.request_endpoint, **self.client_method_args)


class HttpGet(BaseHttpMethodTests, TestCase):
    """Tests for the `http_get` method."""

    request_type = 'get'
    client_method_name = 'http_get'
    client_method_args = {'params': {"key": "value"}, 'timeout': 10}


class HttpPost(BaseHttpMethodTests, TestCase):
    """Tests for the `http_post` method."""

    request_type = 'post'
    client_method_name = 'http_post'
    client_method_args = {'data': {"key": "value"}, 'timeout': 10}


class HttpPatch(BaseHttpMethodTests, TestCase):
    """Tests for the `http_patch` method."""

    request_type = 'patch'
    client_method_name = 'http_patch'
    client_method_args = {'data': {"key": "value"}, 'timeout': 10}


class HttpPut(BaseHttpMethodTests, TestCase):
    """Tests for the `http_put` method."""

    request_type = 'put'
    client_method_name = 'http_put'
    client_method_args = {'data': {"key": "value"}, 'timeout': 10}


class HttpDelete(BaseHttpMethodTests, TestCase):
    """Tests for the `http_delete` method."""

    request_type = 'delete'
    client_method_name = 'http_delete'
    client_method_args = {'timeout': 10}
