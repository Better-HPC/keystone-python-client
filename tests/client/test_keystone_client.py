"""Tests for CRUD operations."""

import re
from unittest import TestCase

from requests import HTTPError

from keystone_client import KeystoneClient
from tests import API_HOST, API_PASSWORD
from .. import API_USER


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


class Create(TestCase):
    """Test record creation via the `create_cluster` method"""

    def setUp(self) -> None:
        """Authenticate a new API client instance"""

        self.client = KeystoneClient(API_HOST)
        self.client.login(API_USER, API_PASSWORD)

    def tearDown(self) -> None:
        """Delete any test records"""

        for cluster in self.client.http_get(f'allocations/clusters/', params={'name': 'Test-Cluster'}).json():
            self.client.http_delete(f"allocations/clusters/{cluster['id']}").raise_for_status()

    def test_record_is_created(self) -> None:
        """Test a record is created successfully"""

        new_record_data = self.client.create_cluster(
            name='Test-Cluster',
            description='Cluster created for testing purposes.'
        )

        pk = new_record_data['id']
        self.client.http_get(f'allocations/clusters/{pk}').raise_for_status()

    def test_record_data_matches_request(self) -> None:
        """Test the returned record data matches the request"""

        expected_data = {'name': 'Test-Cluster', 'description': 'Cluster created for testing purposes.'}
        new_record_data = self.client.create_cluster(**expected_data)

        self.assertEqual(expected_data['name'], new_record_data['name'])
        self.assertEqual(expected_data['description'], new_record_data['description'])
        self.assertFalse(new_record_data['enabled'])

    def test_error_on_failure(self) -> None:
        """Test an error is raised when record creation fails"""

        with self.assertRaises(HTTPError):
            self.client.create_cluster()


class Retrieve(TestCase):
    """Test record retrieval via the `retrieve_cluster` method"""

    def setUp(self) -> None:
        """Set up a test client and create records for testing"""

        self.client = KeystoneClient(API_HOST)
        self.client.login(API_USER, API_PASSWORD)
        self.test_cluster = self.client.create_cluster(
            name='Test-Cluster',
            description='Cluster created for retrieval testing purposes.'
        )

        self.other_cluster = self.client.create_cluster(
            name='Other-Cluster',
            description='Another cluster created for testing purposes.'
        )

    def tearDown(self) -> None:
        """Delete any test records"""

        for cluster in self.client.http_get(f'allocations/clusters/', params={'name': 'Test-Cluster'}).json():
            self.client.http_delete(f"allocations/clusters/{cluster['id']}").raise_for_status()

        for cluster in self.client.http_get(f'allocations/clusters/', params={'name': 'Other-Cluster'}).json():
            self.client.http_delete(f"allocations/clusters/{cluster['id']}").raise_for_status()

    def test_retrieve_by_pk(self) -> None:
        """Test the retrieval of a specific record via its primary key"""

        pk = self.test_cluster['id']
        retrieved_cluster = self.client.retrieve_cluster(pk=pk)
        self.assertIsNotNone(retrieved_cluster)
        self.assertEqual(retrieved_cluster['id'], pk)

    def test_retrieve_by_filters(self) -> None:
        """Test the filtering of returned records via search params"""

        retrieved_clusters = self.client.retrieve_cluster(filters={"name": "Test-Cluster"})
        self.assertIsInstance(retrieved_clusters, list)
        self.assertTrue(all(cluster['name'] == "Test-Cluster" for cluster in retrieved_clusters))

    def test_retrieve_all(self) -> None:
        """Test the retrieval of all records"""

        all_clusters = self.client.retrieve_cluster()
        self.assertIsInstance(all_clusters, list)
        self.assertGreater(len(all_clusters), 0)

    def test_none_on_missing_record(self) -> None:
        """Test `None` is returned when a record does not exist"""

        missing_cluster = self.client.retrieve_cluster(pk=999999)
        self.assertIsNone(missing_cluster)

    def test_error_on_failure(self) -> None:
        """Test an error is raised when record retrieval fails"""

        # Use an unauthenticated client session on an endpoint requiring authentication
        with self.assertRaises(HTTPError):
            KeystoneClient(API_HOST).retrieve_cluster()


class Update(TestCase):
    """Test record updates via the `update_cluster` method"""

    def setUp(self) -> None:
        """Set up a test client and create records for testing"""

        self.client = KeystoneClient(API_HOST)
        self.client.login(API_USER, API_PASSWORD)
        self.test_cluster = self.client.create_cluster(
            name='Test-Cluster',
            description='Cluster created for update testing purposes.'
        )

    def tearDown(self) -> None:
        """Delete any test records"""

        for cluster in self.client.http_get(f'allocations/clusters/', params={'name': 'Test-Cluster'}).json():
            self.client.http_delete(f"allocations/clusters/{cluster['id']}").raise_for_status()

    def test_update_record(self) -> None:
        """Test the record is updated successfully"""

        pk = self.test_cluster['id']
        updated_data = {'description': "Updated description"}
        updated_record = self.client.update_cluster(pk=pk, data=updated_data)
        self.assertIsNotNone(updated_record)
        self.assertEqual(updated_record['description'], "Updated description")

    def test_update_nonexistent_record(self) -> None:
        """Test updating a nonexistent record raises an error"""

        with self.assertRaises(HTTPError):
            self.client.update_cluster(pk=999999, data={'description': "This should fail"})

    def test_partial_update(self) -> None:
        """Test a partial update modifies only specified fields"""

        pk = self.test_cluster['id']
        original_status = self.test_cluster['enabled']

        updated_data = {'description': "Partially updated description"}
        updated_record = self.client.update_cluster(pk=pk, data=updated_data)

        self.assertEqual(updated_record['description'], "Partially updated description")
        self.assertEqual(updated_record['enabled'], original_status)

    def test_no_update_on_empty_data(self) -> None:
        """Test an empty update request does not change the record"""

        pk = self.test_cluster['id']
        original_data = self.test_cluster.copy()
        updated_record = self.client.update_cluster(pk=pk, data={})
        self.assertEqual(updated_record, original_data)


class Delete(TestCase):
    """Test record deletion via the `delete_cluster` method"""

    def setUp(self) -> None:
        """Set up the test client and log in"""

        self.client = KeystoneClient(API_HOST)
        self.client.login(API_USER, API_PASSWORD)
        self.test_cluster = self.client.create_cluster(
            name='Test-Cluster',
            description='Cluster created for delete testing purposes.'
        )

    def tearDown(self) -> None:
        """Clean up by deleting existing test clusters"""

        for cluster in self.client.http_get(f'allocations/clusters/', params={'name': 'Test-Cluster'}).json():
            self.client.http_delete(f"allocations/clusters/{cluster['id']}").raise_for_status()

    def test_delete_record(self) -> None:
        """Test a record is deleted successfully"""

        pk = self.test_cluster['id']
        self.client.delete_cluster(pk=pk)
        retrieved_cluster = self.client.retrieve_cluster(pk=pk)
        self.assertIsNone(retrieved_cluster)

    def test_delete_nonexistent_record_silent(self) -> None:
        """Test deleting a nonexistent record exits silently"""

        self.client.delete_cluster(pk=999999)

    def test_delete_nonexistent_record_raise(self) -> None:
        """Test deleting a nonexistent record raises an exception when specified"""

        with self.assertRaises(HTTPError):
            self.client.delete_cluster(pk=999999, raise_not_exists=True)
