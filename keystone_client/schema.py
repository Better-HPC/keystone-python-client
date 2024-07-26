"""Schema objects used to define available API endpoints."""

from dataclasses import dataclass, field
from urllib.parse import urljoin


class Endpoint(str):

    def join_url(self, base: str, *append) -> str:
        """Join the endpoint with a base URL

        This method returns URLs in a format that avoids trailing slash
        redirects from the Keystone API.

        Args:
            base: The base URL
            *append: Partial paths to append onto the url

        Returns:
            The base URL join with the endpoint
        """

        base = urljoin(base, self)
        for partial_path in append:
            base = urljoin(base, partial_path)

        return base.rstrip('/') + '/'


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

    auth: AuthSchema = field(default_factory=AuthSchema)
    data: DataSchema = field(default_factory=DataSchema)
