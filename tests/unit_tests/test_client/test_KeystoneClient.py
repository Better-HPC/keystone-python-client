"""Unit tests for the `KeystoneClient` class."""

import json
from unittest import TestCase

import httpx

from keystone_client import KeystoneClient


class LoginMethod(TestCase):
    """Test the structure of API login requests."""

    def setUp(self) -> None:
        """Define common test variables."""

        self.api_url = "https://api.example.com"
        self.username = "username123"
        self.password = "password456"

    def test_credentials_sent_to_endpoint(self) -> None:
        """Verify user credentials are posted to the login endpoint."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept and test HTTP requests."""

            url_path = request.url.path.strip('/')
            payload = json.loads(request.content.decode())

            self.assertEqual('POST', request.method)
            self.assertEqual(KeystoneClient.LOGIN_ENDPOINT, url_path)
            self.assertEqual({"username": self.username, "password": self.password}, payload)

            return httpx.Response(200)

        client = KeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        client.login(self.username, self.password)

    def test_http_error_is_raised(self) -> None:
        """Verify an error is raised for a non-200 response."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept HTTP requests and return a 401 error."""

            return httpx.Response(401, json={"detail": "Unauthorized"})

        client = KeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        with self.assertRaises(httpx.HTTPStatusError):
            client.login("user", "pass")


class LogoutMethod(TestCase):
    """Test the structure of API logout requests."""

    def setUp(self) -> None:
        """Define common test variables."""

        self.api_url = "https://api.example.com"

    def test_credentials_sent_to_endpoint(self) -> None:
        """Verify a POST request is made to the logout endpoint."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept and test HTTP requests."""

            url_path = request.url.path.strip('/')

            self.assertEqual('POST', request.method)
            self.assertEqual(KeystoneClient.LOGOUT_ENDPOINT, url_path)

            return httpx.Response(200)

        client = KeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        client.logout()

    def test_http_error_is_raised(self) -> None:
        """Verify an error is raised for a non-200 response."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept HTTP requests and return a 400 error."""

            return httpx.Response(400)

        client = KeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        with self.assertRaises(httpx.HTTPStatusError):
            client.logout()


class IsAuthenticatedMethod(TestCase):
    """Test the structure of requests to verify authentication status."""

    def setUp(self) -> None:
        """Define common test variables."""

        self.api_url = "https://api.example.com"

    def test_successful_response(self) -> None:
        """Verify a GET request is made and user metadata is returned."""

        expected_data = {"user_id": 42, "username": "testuser"}

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept and test HTTP requests."""

            url_path = request.url.path.strip('/')

            self.assertEqual('GET', request.method)
            self.assertEqual(KeystoneClient.IDENTITY_ENDPOINT, url_path)

            return httpx.Response(200, json=expected_data)

        client = KeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        result = client.is_authenticated()
        self.assertEqual(result, expected_data)

    def test_unauthenticated_returns_none(self) -> None:
        """Verify `None` is returned for 401 response."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept HTTP requests and return 401 Unauthorized."""

            return httpx.Response(401, json={"detail": "Unauthorized"})

        client = KeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        result = client.is_authenticated()
        self.assertIsNone(result)

    def test_http_error_is_raised(self) -> None:
        """Verify an error is raised for non-401, non-200 responses."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept HTTP requests and return a 500 error."""

            return httpx.Response(500, json={"detail": "Internal Server Error"})

        client = KeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))

        with self.assertRaises(httpx.HTTPStatusError):
            client.is_authenticated()
