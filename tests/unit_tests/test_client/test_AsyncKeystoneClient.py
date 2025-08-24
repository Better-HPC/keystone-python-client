"""Unit tests for the `AsyncKeystoneClient` class."""

import json
from unittest import IsolatedAsyncioTestCase

import httpx

from keystone_client import AsyncKeystoneClient


class LoginMethod(IsolatedAsyncioTestCase):
    """Test the structure of API login requests."""

    async def asyncSetUp(self) -> None:
        """Define common test variables."""

        self.api_url = "https://api.example.com"
        self.username = "username123"
        self.password = "password456"

    async def test_credentials_sent_to_endpoint(self) -> None:
        """Verify user credentials are posted to the login endpoint."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept and test HTTP requests."""

            url_path = request.url.path.strip('/')
            payload = json.loads(request.content.decode())

            self.assertEqual('POST', request.method)
            self.assertEqual(AsyncKeystoneClient.LOGIN_ENDPOINT, url_path)
            self.assertEqual({"username": self.username, "password": self.password}, payload)

            return httpx.Response(200)

        client = AsyncKeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        await client.login(self.username, self.password)

    async def test_http_error_is_raised(self) -> None:
        """Verify an error is raised for a non-200 response."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept HTTP requests and return a 401 error."""

            return httpx.Response(401, json={"detail": "Unauthorized"})

        client = AsyncKeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        with self.assertRaises(httpx.HTTPStatusError):
            await client.login("user", "pass")


class LogoutMethod(IsolatedAsyncioTestCase):
    """Test the structure of API logout requests."""

    async def asyncSetUp(self) -> None:
        """Define common test variables."""

        self.api_url = "https://api.example.com"

    async def test_credentials_sent_to_endpoint(self) -> None:
        """Verify a POST request is made to the logout endpoint."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept and test HTTP requests."""

            url_path = request.url.path.strip('/')

            self.assertEqual('POST', request.method)
            self.assertEqual(AsyncKeystoneClient.LOGOUT_ENDPOINT, url_path)

            return httpx.Response(200)

        client = AsyncKeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        await client.logout()

    async def test_http_error_is_raised(self) -> None:
        """Verify an error is raised for a non-200 response."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept HTTP requests and return a 400 error."""

            return httpx.Response(400)

        client = AsyncKeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        with self.assertRaises(httpx.HTTPStatusError):
            await client.logout()


class IsAuthenticatedMethod(IsolatedAsyncioTestCase):
    """Test the structure of requests to verify authentication status."""

    async def asyncSetUp(self) -> None:
        """Define common test variables."""

        self.api_url = "https://api.example.com"

    async def test_successful_response(self) -> None:
        """Verify a GET request is made and user metadata is returned."""

        expected_data = {"user_id": 42, "username": "testuser"}

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept and test HTTP requests."""

            url_path = request.url.path.strip('/')

            self.assertEqual('GET', request.method)
            self.assertEqual(AsyncKeystoneClient.IDENTITY_ENDPOINT, url_path)

            return httpx.Response(200, json=expected_data)

        client = AsyncKeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        result = await client.is_authenticated()
        self.assertEqual(result, expected_data)

    async def test_unauthenticated_returns_none(self) -> None:
        """Verify `None` is returned for 401 response."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept HTTP requests and return 401 Unauthorized."""

            return httpx.Response(401, json={"detail": "Unauthorized"})

        client = AsyncKeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))
        result = await client.is_authenticated()
        self.assertIsNone(result)

    async def test_http_error_is_raised(self) -> None:
        """Verify an error is raised for non-401, non-200 responses."""

        def handler(request: httpx.Request) -> httpx.Response:
            """Intercept HTTP requests and return a 500 error."""

            return httpx.Response(500, json={"detail": "Internal Server Error"})

        client = AsyncKeystoneClient(base_url=self.api_url, transport=httpx.MockTransport(handler))

        with self.assertRaises(httpx.HTTPStatusError):
            await client.is_authenticated()
