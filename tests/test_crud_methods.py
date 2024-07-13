"""Tests for CRUD operations."""

from unittest import TestCase

from keystone_client import KeystoneClient


class Retrieve(TestCase):
    """Tests for retrieve methods"""

    def test_methods_exist(self) -> None:
        """Test a method exists for each endpoint in the class schema"""

        client = KeystoneClient('http://test.domain.com')
        for endpoint in KeystoneClient.schema._fields:
            method_name = f'retrieve_{endpoint}'
            self.assertTrue(hasattr(client, method_name), f'Method does not exist {method_name}')
