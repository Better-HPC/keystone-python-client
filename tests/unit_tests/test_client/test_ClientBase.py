"""Unit tests for the `ClientBase` class."""

from unittest import TestCase
from unittest.mock import MagicMock

from keystone_client.client import ClientBase


class DummyClientBase(ClientBase):
    """Concrete subclass of ClientBase for testing."""

    def login(self, username: str, password: str, timeout: int) -> None:
        """Method required by abstract parent for authenticating a user session."""

    def logout(self) -> None:
        """Method required by abstract parent for terminating a user session."""

    def whoami(self) -> dict:
        """Method required by abstract parent for returning user metadata."""

        return {}


class IsAuthenticatedMethod(TestCase):
    """Tests the `is_authenticated` method.

    Verifies the returned value reflects whether metadata is available for
    the current user session.
    """

    def test_returns_true_for_populated_metadata(self) -> None:
        """Verify a truthy result is returned when `whoami` returns metadata."""

        client = DummyClientBase()
        client.whoami = MagicMock(return_value={"user_id": 42})
        self.assertTrue(client.is_authenticated())

    def test_returns_false_for_empty_metadata(self) -> None:
        """Verify a falsy result is returned when `whoami` returns no metadata."""

        client = DummyClientBase()
        client.whoami = MagicMock(return_value={})
        self.assertFalse(client.is_authenticated())
