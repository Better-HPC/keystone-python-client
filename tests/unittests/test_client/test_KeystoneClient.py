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
        """Verify user credentials are posted to the authentication endpoint."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept and test HTTP requests."""

            payload = json.loads(request.content.decode())
            self.assertEqual('POST', request.method)
            self.assertEqual({"username": self.username, "password": self.password}, payload)
            return httpx.Response(200)

        client = KeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        client.login(self.username, self.password)

    def test_login_http_error(self) -> None:
        """Verify an error is raised for a non-200 response."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept HTTP requests and return a 401 error."""

            return httpx.Response(401, json={"detail": "Unauthorized"})

        client = KeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        with self.assertRaises(httpx.HTTPStatusError) as raised_error:
            client.login("user", "pass")
            self.assertEqual(raised_error.exception.response.status_code, 401)
