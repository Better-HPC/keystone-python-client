"""Schema objects used to define available API endpoints."""

from dataclasses import dataclass
from urllib.parse import urljoin


class Endpoint(str):

    def join_url(self, url: str) -> str:
        """Join the endpoint with a base URL

        This method returns URLs in a format that avoids trailing slash
        redirects from the Keystone API.

        Args:
            url: The base URL

        Returns:
            The base URL join with the endpoint
        """

        return urljoin(url, self).rstrip('/') + '/'


@dataclass
class AuthSchema:
    """Schema defining API endpoints used for JWT authentication"""

    new: Endpoint = Endpoint("authentication/new")
    refresh: Endpoint = Endpoint("authentication/refresh")
    blacklist: Endpoint = Endpoint("authentication/blacklist")


@dataclass
class DataSchema:
    """Schema defining API endpoints for data access"""

    allocations: Endpoint = Endpoint("allocations/allocations")
    requests: Endpoint = Endpoint("allocations/requests")
    research_groups: Endpoint = Endpoint("users/researchgroups")
    users: Endpoint = Endpoint("users/users")


@dataclass
class Schema:
    """Schema defining the complete set of API endpoints"""

    auth: AuthSchema = AuthSchema()
    data: DataSchema = DataSchema()
