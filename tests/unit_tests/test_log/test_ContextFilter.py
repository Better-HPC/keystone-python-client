"""Unit tests for the `ContextFilter` class."""

import logging
from logging import LogRecord
from unittest import TestCase

from keystone_client.log import ContextFilter


class FilterMethod(TestCase):
    """Verify the assignment of default attributes by the `filter` method."""

    @staticmethod
    def _create_log_record() -> LogRecord:
        """Create a log record with dummy data."""

        return LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="test message",
            args=(),
            exc_info=None
        )

    def test_missing_attributes_are_added(self) -> None:
        """Verify missing attributes are added and assigned empty strings."""

        record = self._create_log_record()
        ContextFilter().filter(record)

        # Ensure required attributes exist after being processed
        self.assertTrue(hasattr(record, "cid"))
        self.assertTrue(hasattr(record, "baseurl"))
        self.assertTrue(hasattr(record, "method"))
        self.assertTrue(hasattr(record, "endpoint"))
        self.assertTrue(hasattr(record, "url"))

        # All missing values should be empty strings
        self.assertEqual("", record.cid)
        self.assertEqual("", record.baseurl)
        self.assertEqual("", record.method)
        self.assertEqual("", record.endpoint)
        self.assertEqual("", record.url)

    def test_existing_attributes_are_preserved(self) -> None:
        """Verify existing attributes are not overwritted."""

        record = self._create_log_record()
        record.cid = "123"
        record.baseurl = "http://x"
        record.method = "GET"

        ContextFilter().filter(record)

        # Existing attributes should not change
        self.assertEqual("123", record.cid)
        self.assertEqual("http://x", record.baseurl)
        self.assertEqual("GET", record.method)

        # Missing attributes should be added
        self.assertEqual("", record.endpoint)
        self.assertEqual("", record.url)

    def test_filter_always_returns_true(self) -> None:
        """Verify the returned value is true."""

        record = self._create_log_record()
        result = ContextFilter().filter(record)
        self.assertTrue(result)
