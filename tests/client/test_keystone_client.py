"""Tests for CRUD operations."""

import re
from dataclasses import asdict
from unittest import TestCase

from keystone_client import KeystoneClient
from keystone_client.schema import Schema
from tests import API_HOST


class APIVersion(TestCase):
    """Tests for the `api_version` method"""

    def test_version_is_returned(self) -> None:
        """Test a version number is returned"""

        # Simplified version identification from PEP 440
        version_regex = re.compile(r"""
            ^
            (?P<major>[0-9]+)\.       # Major version number
            (?P<minor>[0-9]+)\.       # Minor version number
            (?P<patch>[0-9]+)         # Patch version number
            (?:\.                     # Optional dot
            (?P<suffix>[a-zA-Z0-9]+)  # Optional suffix (letters or numbers)
            )?                        # Make the entire suffix part optional
            $
        """, re.VERBOSE)

        client = KeystoneClient(API_HOST)
        self.assertRegex(client.api_version, version_regex)
