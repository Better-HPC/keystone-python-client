"""Tests for the `HTTPClient` class"""

import unittest
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
class HttpGet(unittest.TestCase):
    """Tests for the `http_get` method"""

    def setUp(self) -> None:
        """Set up variables and a client instance for each test case"""

        self.client = HTTPClient(API_HOST)
        self.endpoint_str = "/test-endpoint"
        self.params = {"key": "value"}
        self.timeout = 10

    def test_unauthenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_get` method for a successful, unauthenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.http_get(self.endpoint_str, params=self.params, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "get",
            urljoin(self.client.url, self.endpoint_str),
            params=self.params,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_authenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_get` method for a successful, authenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.login(API_USER, API_PASSWORD)
        self.client.http_get(self.endpoint_str, params=self.params, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "get",
            urljoin(self.client.url, self.endpoint_str),
            params=self.params,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_http_get_error(self, mock_request: Mock) -> None:
        """Test the `http_get` method for a failed request"""

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error")
        mock_request.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            self.client.http_get(self.endpoint_str, params=self.params, timeout=self.timeout)

        mock_request.assert_called_once_with(
            "get",
            urljoin(self.client.url, self.endpoint_str),
            params=self.params,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()


@patch('requests.request')
class HttpPost(TestCase):
    """Tests for the `http_post` method"""

    def setUp(self) -> None:
        """Set up variables and a client instance for each test case"""

        self.client = HTTPClient(API_HOST)
        self.endpoint_str = "/test-endpoint"
        self.data = {"key": "value"}
        self.timeout = 10

    def test_unauthenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_post` method for a successful, unauthenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.http_post(self.endpoint_str, data=self.data, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "post",
            urljoin(self.client.url, self.endpoint_str),
            data=self.data,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_authenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_post` method for a successful, authenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.login(API_USER, API_PASSWORD)
        self.client.http_post(self.endpoint_str, data=self.data, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "post",
            urljoin(self.client.url, self.endpoint_str),
            data=self.data,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_http_post_error(self, mock_request: Mock) -> None:
        """Test the `http_post` method for a failed request"""

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error")
        mock_request.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            self.client.http_post(self.endpoint_str, data=self.data, timeout=self.timeout)

        mock_request.assert_called_once_with(
            "post",
            urljoin(self.client.url, self.endpoint_str),
            data=self.data,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()


@patch('requests.request')
class HttpPatch(TestCase):
    """Tests for the `http_patch` method"""

    def setUp(self) -> None:
        """Set up variables and a client instance for each test case"""

        self.client = HTTPClient(API_HOST)
        self.endpoint_str = "/test-endpoint"
        self.data = {"key": "value"}
        self.timeout = 10

    def test_unauthenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_patch` method for a successful, unauthenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.http_patch(self.endpoint_str, data=self.data, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "patch",
            urljoin(self.client.url, self.endpoint_str),
            data=self.data,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_authenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_patch` method for a successful, authenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.login(API_USER, API_PASSWORD)
        self.client.http_patch(self.endpoint_str, data=self.data, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "patch",
            urljoin(self.client.url, self.endpoint_str),
            data=self.data,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_http_patch_error(self, mock_request: Mock) -> None:
        """Test the `http_patch` method for a failed request"""

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error")
        mock_request.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            self.client.http_patch(self.endpoint_str, data=self.data, timeout=self.timeout)

        mock_request.assert_called_once_with(
            "patch",
            urljoin(self.client.url, self.endpoint_str),
            data=self.data,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()


@patch('requests.request')
class HttpPut(TestCase):
    """Tests for the `http_put` method"""

    def setUp(self) -> None:
        """Set up variables and a client instance for each test case"""

        self.client = HTTPClient(API_HOST)
        self.endpoint_str = "/test-endpoint"
        self.data = {"key": "value"}
        self.timeout = 10

    def test_unauthenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_put` method for a successful, unauthenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.http_put(self.endpoint_str, data=self.data, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "put",
            urljoin(self.client.url, self.endpoint_str),
            data=self.data,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_authenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_put` method for a successful, authenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.login(API_USER, API_PASSWORD)
        self.client.http_put(self.endpoint_str, data=self.data, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "put",
            urljoin(self.client.url, self.endpoint_str),
            data=self.data,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_http_put_error(self, mock_request: Mock) -> None:
        """Test the `http_put` method for a failed request"""

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error")
        mock_request.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            self.client.http_put(self.endpoint_str, data=self.data, timeout=self.timeout)

        mock_request.assert_called_once_with(
            "put",
            urljoin(self.client.url, self.endpoint_str),
            data=self.data,
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()


@patch('requests.request')
class HttpDelete(TestCase):
    """Tests for the `http_delete` method"""

    def setUp(self) -> None:
        """Set up variables and a client instance for each test case"""

        self.client = HTTPClient(API_HOST)
        self.endpoint_str = "/test-endpoint"
        self.timeout = 10

    def test_unauthenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_delete` method for a successful, unauthenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.http_delete(self.endpoint_str, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "delete",
            urljoin(self.client.url, self.endpoint_str),
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_authenticated_request(self, mock_request: Mock) -> None:
        """Test the `http_delete` method for a successful, authenticated request"""

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        self.client.login(API_USER, API_PASSWORD)
        self.client.http_delete(self.endpoint_str, timeout=self.timeout)
        mock_request.assert_called_once_with(
            "delete",
            urljoin(self.client.url, self.endpoint_str),
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()

    def test_http_delete_error(self, mock_request: Mock) -> None:
        """Test the `http_delete` method for a failed request"""

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error")
        mock_request.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            self.client.http_delete(self.endpoint_str, timeout=self.timeout)

        mock_request.assert_called_once_with(
            "delete",
            urljoin(self.client.url, self.endpoint_str),
            headers=self.client._auth.get_auth_headers(),
            timeout=self.timeout
        )
        mock_response.raise_for_status.assert_called_once()
