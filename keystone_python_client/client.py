from typing import *

__all__ = ['KeystoneClient']


class KeystoneClient:
    """Client class for submitting requests to the Keystone API"""

    def __init__(self, url: str) -> None:
        """Initialize the class

        Args:
            url: The base API URL
        """

        self.url = url
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
