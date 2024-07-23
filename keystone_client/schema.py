"""Schema objects used to define available API endpoints."""

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
