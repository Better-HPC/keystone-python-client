"""Test the sending of HTTP requests."""

from unittest import TestCase

from keystone_client.http import HTTPClient
from tests.http.common import CommonHttpMethodTests


class BaseUrlProperty(TestCase):
    """Tests for the `base_url` property."""

    def test_trailing_slash_enforced(self) -> None:
        """Test the URL is returned with a single trailing slash."""

        base_url = 'https://test.domain.com'
        expected_url = base_url + '/'

        # Test for various numbers of trailing slashes provided at init
        self.assertEqual(expected_url, HTTPClient(base_url).base_url)
        self.assertEqual(expected_url, HTTPClient(base_url + '/').base_url)
        self.assertEqual(expected_url, HTTPClient(base_url + '////').base_url)


class HttpGet(CommonHttpMethodTests, TestCase):
    """Tests for the `http_get` method."""

    request_type = 'get'
    method_name = 'http_get'
    method_args = {'params': {"key": "value"}, 'timeout': 10}


class HttpPost(CommonHttpMethodTests, TestCase):
    """Tests for the `http_post` method."""

    request_type = 'post'
    method_name = 'http_post'
    method_args = {'data': {"key": "value"}, 'timeout': 10}


class HttpPatch(CommonHttpMethodTests, TestCase):
    """Tests for the `http_patch` method."""

    request_type = 'patch'
    method_name = 'http_patch'
    method_args = {'data': {"key": "value"}, 'timeout': 10}


class HttpPut(CommonHttpMethodTests, TestCase):
    """Tests for the `http_put` method."""

    request_type = 'put'
    method_name = 'http_put'
    method_args = {'data': {"key": "value"}, 'timeout': 10}


class HttpDelete(CommonHttpMethodTests, TestCase):
    """Tests for the `http_delete` method."""

    request_type = 'delete'
    method_name = 'http_delete'
    method_args = {'timeout': 10}
