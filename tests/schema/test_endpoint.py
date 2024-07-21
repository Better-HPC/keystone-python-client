from unittest import TestCase


# class ResolveEndpoint(TestCase):
#     """Tests for the `resolve_endpoint` method"""
#
#     def test_trailing_slash(self) -> None:
#         """Test rendered endpoints are always resolved with a single trailing slash"""
#
#         client = HTTPClient(url='https://example.com')
#         expected_url = 'https://example.com/api/endpoint/'
#
#         self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint'))
#         self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint/'))
#         self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint//'))
#         self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint//'))
#
#     def test_leading_slash(self) -> None:
#         """Test rendered endpoints resolved correctly regardless of leading slashes"""
#
#         client = HTTPClient(url='https://example.com')
#         expected_url = 'https://example.com/api/endpoint/'
#         self.assertEqual(expected_url, client.resolve_endpoint('api/endpoint/'))
#         self.assertEqual(expected_url, client.resolve_endpoint('/api/endpoint/'))
#         self.assertEqual(expected_url, client.resolve_endpoint('//api/endpoint/'))
#         self.assertEqual(expected_url, client.resolve_endpoint('///api/endpoint/'))
#