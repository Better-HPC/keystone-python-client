"""Function tests for asynchronous CRUD operations."""

from unittest import IsolatedAsyncioTestCase

import httpx

from keystone_client import AsyncKeystoneClient
from tests.function_tests.config import API_HOST, API_PASSWORD, API_USER


class Authentication(IsolatedAsyncioTestCase):
    """Test logging in/out via the `login` and `logout` methods."""

    async def asyncSetUp(self) -> None:
        """Instantiate a new API client instance."""

        self.client = AsyncKeystoneClient(API_HOST)

    async def asyncTearDown(self) -> None:
        """Close any open server connections."""

        await self.client.close()

    async def test_login_logout(self) -> None:
        """Verify users are successfully logged in/out when providing valid credentials."""

        self.assertFalse(await self.client.is_authenticated())

        await self.client.login(API_USER, API_PASSWORD)
        self.assertTrue(await self.client.is_authenticated())

        await self.client.logout()
        self.assertFalse(await self.client.is_authenticated())

    async def test_incorrect_credentials(self) -> None:
        """Verify an error is raised when authenticating with incorrect credentials."""

        with self.assertRaisesRegex(httpx.HTTPError, '400 Bad Request'):
            await self.client.login(API_USER, "This is not a valid password.")

    async def test_logout_unauthenticated(self) -> None:
        """Verify the `logout` method exits silently when logging out an unauthenticated user."""

        self.assertFalse(await self.client.is_authenticated())
        await self.client.logout()
        self.assertFalse(await self.client.is_authenticated())

    async def test_authentication_is_not_shared(self) -> None:
        """Test user authentication is tied to specific instances."""

        client1 = AsyncKeystoneClient(API_HOST)
        client2 = AsyncKeystoneClient(API_HOST)

        await client1.login(API_USER, API_PASSWORD)
        self.assertTrue(await client1.is_authenticated())
        self.assertFalse(await client2.is_authenticated())

        await client1.close()
        await client2.close()


class UserMetadata(IsolatedAsyncioTestCase):
    """Test the fetching of user metadata via the `is_authenticated` method."""

    async def asyncSetUp(self) -> None:
        """Instantiate a new API client instance."""

        self.client = AsyncKeystoneClient(API_HOST)

    async def asyncTearDown(self) -> None:
        """Close any open server connections."""

        await self.client.close()

    async def test_unauthenticated_user(self) -> None:
        """Verify an empty dictionary is returned for an unauthenticated user."""

        self.assertEqual(dict(), await self.client.is_authenticated())

    async def test_authenticated_user(self) -> None:
        """Verify user metadata is returned for an authenticated user."""

        await self.client.login(API_USER, API_PASSWORD)
        user_meta = await self.client.is_authenticated()
        self.assertEqual(API_USER, user_meta['username'])
