"""Function tests for synchronous CRUD operations."""

from unittest import TestCase

import httpx

from keystone_client import KeystoneClient
from tests.function_tests.config import API_HOST, API_PASSWORD, API_USER


class Authentication(TestCase):
    """Test logging in/out via the `login` and `logout` methods."""

    def setUp(self) -> None:
        """Instantiate a new API client instance."""

        self.client = KeystoneClient(API_HOST)

    def tearDown(self) -> None:
        """Close any open server connections."""

        self.client.close()

    def test_login_logout(self) -> None:
        """Verify users are successfully logged in/out when providing valid credentials."""

        self.assertFalse(self.client.is_authenticated())

        self.client.login(API_USER, API_PASSWORD)
        self.assertTrue(self.client.is_authenticated())

        self.client.logout()
        self.assertFalse(self.client.is_authenticated())

    def test_incorrect_credentials(self) -> None:
        """Verify an error is raised when authenticating with incorrect credentials."""

        with self.assertRaisesRegex(httpx.HTTPError, '400 Bad Request'):
            self.client.login(API_USER, "This is not a valid password.")

    def test_logout_unauthenticated(self) -> None:
        """Verify the `logout` method exits silently when logging out an unauthenticated user."""

        self.assertFalse(self.client.is_authenticated())
        self.client.logout()
        self.assertFalse(self.client.is_authenticated())

    def test_authentication_is_not_shared(self) -> None:
        """Test user authentication is tied to specific instances."""

        client1 = KeystoneClient(API_HOST)
        client2 = KeystoneClient(API_HOST)

        client1.login(API_USER, API_PASSWORD)
        self.assertTrue(client1.is_authenticated())
        self.assertFalse(client2.is_authenticated())

        client1.close()
        client2.close()


class UserMetadata(TestCase):
    """Test the fetching of user metadata via the `is_authenticated` method."""

    def setUp(self) -> None:
        """Instantiate a new API client instance."""

        self.client = KeystoneClient(API_HOST)

    def tearDown(self) -> None:
        """Close any open server connections."""

        self.client.close()

    def test_unauthenticated_user(self) -> None:
        """Verify an empty dictionary is returned for an unauthenticated user."""

        self.assertEqual(dict(), self.client.is_authenticated())

    def test_authenticated_user(self) -> None:
        """Verify user metadata is returned for an authenticated user."""

        self.client.login(API_USER, API_PASSWORD)
        user_meta = self.client.is_authenticated()
        self.assertEqual(API_USER, user_meta['username'])
