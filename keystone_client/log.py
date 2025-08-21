"""Components for integrating with the standard Python logging system.

The `log` module defines extensions to Python’s logging framework that
extend log records with application-specific context. These components
are initialized automatically with the package and are not intended
for direct import.
"""

import logging


class ContextFilter(logging.Filter):
    """Logging filter used to ensure standard application values exist for all log records.

    Attributes enforced by this filter:
        - cid
        - baseurl
        - method
        - endpoint
        - url
    """

    def filter(self, record) -> True:
        """Ensure a log record has all required contextual attributes.

        Args:
            record: The log record to process.

        Returns:
           Always returns `True`.
        """

        for attr in ("cid", "baseurl", "method", "endpoint", "url"):
            if not hasattr(record, attr):
                setattr(record, attr, "")

        # Return `True` to indicate the record should be logged
        return True
