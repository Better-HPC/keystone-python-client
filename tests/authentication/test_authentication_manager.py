"""Tests for the `AuthenticationManager` class."""

from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import Mock, patch

import jwt
import requests
from requests.exceptions import HTTPError

from keystone_client.authentication import AuthenticationManager, JWT
from tests import API_HOST, API_PASSWORD, API_USER


def create_token(access_expires: datetime, refresh_expires: datetime) -> JWT:
    """Create a JWT token

    Args:
        access_expires: The expiration datetime for the access token
        refresh_expires: The expiration datetime for the refresh token

    Returns:
        A JWT instance with the given expiration dates
    """

    return JWT(
        access=jwt.encode({'exp': access_expires.timestamp()}, 'secret'),
        refresh=jwt.encode({'exp': refresh_expires.timestamp()}, 'secret')
    )


class IsAuthenticated(TestCase):
    """Tests for the `is_authenticated` method"""

    def test_not_authenticated(self) -> None:
        """Test the return value is `false` when the manager has no JWT data"""

        manager = AuthenticationManager(API_HOST)
        self.assertIsNone(manager.jwt)
        self.assertFalse(manager.is_authenticated())

    def test_valid_jwt(self) -> None:
        """Test the return value is `True` when the JWT token is not expired"""

        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() + timedelta(hours=1),
            refresh_expires=datetime.now() + timedelta(days=1)
        )

        self.assertTrue(manager.is_authenticated())

    def test_refreshable_jwt(self) -> None:
        """Test the return value is `True` when the JWT token expired but refreshable"""

        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() - timedelta(hours=1),
            refresh_expires=datetime.now() + timedelta(days=1)
        )

        self.assertTrue(manager.is_authenticated())

    def test_expired_jwt(self) -> None:
        """Test the return value is `False` when the JWT token is expired"""

        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() - timedelta(days=1),
            refresh_expires=datetime.now() - timedelta(hours=1)
        )

        self.assertFalse(manager.is_authenticated())


class GetAuthHeaders(TestCase):
    """Tests for the `get_auth_headers` method"""

    def test_not_authenticated(self) -> None:
        """Test the returned headers are empty when not authenticated"""

        manager = AuthenticationManager(API_HOST)
        headers = manager.get_auth_headers()
        self.assertEqual(dict(), headers)

    def test_headers_match_jwt(self) -> None:
        """Test the returned data matches the JWT token"""

        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() + timedelta(hours=1),
            refresh_expires=datetime.now() + timedelta(days=1)
        )

        headers = manager.get_auth_headers()
        self.assertEqual(f"Bearer {manager.jwt.access}", headers["Authorization"])


class Login(TestCase):
    """Test session authentication via the `login` method"""

    def test_with_correct_credentials(self) -> None:
        """Test users are successfully logged in/out when providing correct credentials"""

        manager = AuthenticationManager(API_HOST)
        self.assertFalse(manager.is_authenticated())

        manager.login(API_USER, API_PASSWORD)
        self.assertTrue(manager.is_authenticated())

    def test_with_incorrect_credentials(self) -> None:
        """Test an error is raised when authenticating with invalid credentials"""

        manager = AuthenticationManager(API_HOST)
        with self.assertRaises(HTTPError) as error:
            manager.login('foo', 'bar')
            self.assertEqual(401, error.response.status_code)

    @patch('requests.post')
    def test_jwt_credentials_are_cached(self, mock_post: Mock) -> None:
        """Test JWT credentials are cached after a successful login"""

        # Mock response for successful login
        mock_response = Mock()
        mock_response.json.return_value = {
            'access': 'fake_access_token',
            'refresh': 'fake_refresh_token'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Call the login method
        manager = AuthenticationManager(API_HOST)
        manager.login(API_USER, API_PASSWORD)

        # Assertions to check if tokens are set correctly
        self.assertIsNotNone(manager.jwt)
        self.assertEqual(manager.jwt.access, 'fake_access_token')
        self.assertEqual(manager.jwt.refresh, 'fake_refresh_token')


class Logout(TestCase):
    """Test session invalidation via the `logout` method"""

    def setUp(self) -> None:
        """Authenticate a new `AuthenticationManager` instance"""

        self.manager = AuthenticationManager(API_HOST)
        self.manager.login(API_USER, API_PASSWORD)

    def test_user_is_logged_out(self) -> None:
        """Test the credentials are cleared and the user is logged out"""

        self.manager.logout()
        self.assertFalse(self.manager.is_authenticated())
        self.assertIsNone(self.manager.jwt)

    @patch('requests.post')
    def test_blacklist_request_sent(self, mock_post):
        """Test a blacklist request is sent to the API server"""

        refresh_token = self.manager.jwt.refresh
        blacklist_url = self.manager.blacklist_url

        self.manager.logout()
        mock_post.assert_called_once_with(
            blacklist_url,
            data={'refresh': refresh_token},
            timeout=None
        )

        self.assertIsNone(self.manager.jwt)

    @patch('requests.post')
    def test_logout_failure(self, mock_post: Mock) -> None:
        """Test an error is raised when the token blacklist request fails"""

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Failed to blacklist token")
        mock_post.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            self.manager.logout()

    @patch('requests.post')
    def test_logout_with_no_jwt(self, mock_post: Mock) -> None:
        """Test the function exits silently when already not authenticated"""

        AuthenticationManager(API_HOST).logout()
        mock_post.assert_not_called()


class Refresh(TestCase):
    """Test credential refreshing via the `refresh` method"""

    def test_refresh_while_not_authenticated(self) -> None:
        """Test the refresh call exits silently when not authenticated"""

        manager = AuthenticationManager(API_HOST)
        self.assertFalse(manager.is_authenticated())
        self.assertIsNone(manager.jwt)

        with patch('requests.post') as mock_post:
            manager.refresh()
            mock_post.assert_not_called()

    def test_refresh_with_valid_access_token(self) -> None:
        """Test the refresh call exits silently when not credentials are not expired"""

        manager = AuthenticationManager(API_HOST)
        manager.login(API_USER, API_PASSWORD)

        with patch('requests.post') as mock_post:
            manager.refresh()
            mock_post.assert_not_called()

    def test_refresh_with_valid_access_token_force(self) -> None:
        """Test the refresh call refreshes valid credentials `force=True`"""

        manager = AuthenticationManager(API_HOST)
        manager.login(API_USER, API_PASSWORD)
        refresh_token = manager.jwt.refresh

        with patch('requests.post') as mock_post:
            manager.refresh(force=True)
            mock_post.assert_called_once_with(
                manager.refresh_url,
                data={'refresh': refresh_token},
                timeout=None
            )

    @patch('requests.post')
    def test_refresh_with_expired_access_token(self, mock_post: Mock) -> None:
        """Test refreshing when the access token is expired"""

        # Mock a session with an expired token
        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() - timedelta(days=1),
            refresh_expires=datetime.now() + timedelta(days=1)
        )
        refresh_token = manager.jwt.refresh

        # Mock response for successful refresh
        mock_response = Mock()
        mock_response.json.return_value = {"refresh": "new_refresh_token"}
        mock_post.return_value = mock_response

        manager.refresh()
        mock_post.assert_called_once_with(
            manager.refresh_url,
            data={'refresh': refresh_token},
            timeout=None
        )

        # Check if refresh token was updated
        self.assertEqual(manager.jwt.refresh, "new_refresh_token")

    @patch('requests.post')
    def test_refresh_with_expired_refresh_token(self, mock_post: Mock) -> None:
        """Test refreshing when the refresh token is expired"""

        # Mock a session with an expired token
        manager = AuthenticationManager(API_HOST)
        manager.jwt = create_token(
            access_expires=datetime.now() - timedelta(days=1),
            refresh_expires=datetime.now() - timedelta(days=1)
        )

        with self.assertRaisesRegex(RuntimeError, "Refresh token has expired. Login again to continue."):
            manager.refresh()

        mock_post.assert_not_called()

    def test_refresh_error(self) -> None:
        """Test an HTTP error is raised when the credential refresh fails"""

        manager = AuthenticationManager(API_HOST)
        manager.login(API_USER, API_PASSWORD)

        with patch('requests.post') as mock_post, self.assertRaises(requests.HTTPError):
            mock_post.side_effect = requests.HTTPError()
            manager.refresh(force=True)
