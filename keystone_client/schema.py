import urllib.parse

from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema, CoreSchema


class Endpoint(str):
    """API endpoint"""

    def __init__(self, endpoint: str) -> None:
        self._endpoint = endpoint.strip('/')

    def resolve(self, url: str) -> str:
        return urllib.parse.urljoin(url, self._endpoint) + '/'

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

    def __str__(self) -> str:
        return self._endpoint


class AuthSchema(BaseModel):
    """Schema defining API endpoints used for JWT authentication"""

    new: Endpoint = Endpoint("authentication/new")
    refresh: Endpoint = Endpoint("authentication/refresh")
    blacklist: Endpoint = Endpoint("authentication/blacklist")


class DataSchema(BaseModel):
    """Schema defining API endpoints used for data access"""

    allocations: Endpoint = Endpoint("allocations/allocations")
    requests: Endpoint = Endpoint("allocations/requests")
    research_groups: Endpoint = Endpoint("users/researchgroups")
    users: Endpoint = Endpoint("users/users")


class Schema(BaseModel):
    """Schema defining the complete set of API endpoints"""

    auth: AuthSchema = AuthSchema()
    data: DataSchema = DataSchema()
