"""Schema objects used to define available API endpoints."""

from urllib.parse import urljoin

from pydantic import BaseModel


class AuthSchema(BaseModel):
    """Schema defining API endpoints used for JWT authentication"""

    new: str = "authentication/new"
    refresh: str = "authentication/refresh"
    blacklist: str = "authentication/blacklist"


class DataSchema(BaseModel):
    """Schema defining API strs endpoints for data access"""

    allocations: str = "allocations/allocations"
    requests: str = "allocations/requests"
    research_groups: str = "users/researchgroups"
    users: str = "users/users"


class Schema(BaseModel):
    """Schema defining the complete set of API endpoints"""

    auth: AuthSchema = AuthSchema()
    data: DataSchema = DataSchema()

    def join(self, url: str, endpoint: str) -> str:
        """Join a base URL with an endpoint to form a complete URL

        This method returns URLs in a format that avoids trailing slash
        redirects from the Keystone API.

        Args:
            url: The base URL
            endpoint: The endpoint to be appended to the base URL.

        Returns:
            The base URL join with the endpoint
        """

        return urljoin(url, endpoint).rstrip('/') + '/'
