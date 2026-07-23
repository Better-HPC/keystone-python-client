"""Unit tests for the `DefaultContextAdapter` class."""

import unittest
from logging import Logger

from keystone_client.log import DefaultContextAdapter


class ProcessMethod(unittest.TestCase):
    """Tests the `process` method.

    Verifies that the log message and its context values are merged
    correctly, with values explicitly provided by the caller always
    taking precedence over the adapter's defaults.
    """

    def setUp(self) -> None:
        """Instantiate testing fixtures."""

        self.adapter = DefaultContextAdapter(Logger('testLogger'), {"default": "value"})

    def test_injects_default_context(self) -> None:
        """Verify default values are injected into the `kwarg["extras"]`."""

        msg, kwargs = self.adapter.process("test message", {})

        self.assertEqual(msg, "test message")
        self.assertEqual({"extra": {"default": "value"}}, kwargs)

    def test_preserves_existing_extra(self) -> None:
        """Verify non-default values in `kwarg["extras"]` remain unchanged."""

        msg, kwargs = self.adapter.process("test message", {"extra": {"user": "alice"}})

        self.assertEqual(msg, "test message")
        self.assertEqual(kwargs["extra"]["user"], "alice")

    def test_does_not_overwrite_existing_keys(self) -> None:
        """Verify default values do not overwrite existing values."""

        msg, kwargs = self.adapter.process("overwrite check", {"extra": {"default": "custom"}})
        self.assertEqual(kwargs["extra"]["default"], "custom")
