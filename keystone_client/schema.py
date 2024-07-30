"""Schema objects used to define available API endpoints."""

import os.path
from dataclasses import dataclass, field
from os import path


class Endpoint(str):
    """API endpoint agnostic to the baseAPI URL"""

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

        url = os.path.join(base, self)
        for partial_path in filter(lambda x: x is not None, append):
            url = path.join(url, str(partial_path))

        return url.rstrip('/') + '/'


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
    clusters: Endpoint = Endpoint("allocations/clusters")
    requests: Endpoint = Endpoint("allocations/requests")
    research_groups: Endpoint = Endpoint("users/researchgroups")
    users: Endpoint = Endpoint("users/users")


@dataclass
class Schema:
    """Schema defining the complete set of API endpoints"""

    auth: AuthSchema = field(default_factory=AuthSchema)
    data: DataSchema = field(default_factory=DataSchema)
