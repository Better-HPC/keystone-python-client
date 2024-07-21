from pydantic import BaseModel


class AuthSchema(BaseModel):
    new: str = "authentication/new/"
    refresh: str = "authentication/refresh/"
    blacklist: str = "authentication/blacklist/"


class EndpointSchema(BaseModel):
    allocations: str = "allocations/allocations/"
    requests: str = "allocations/requests/"
    research_groups: str = "users/researchgroups/"
    users: str = "users/users/"


class Schema(BaseModel):
    auth: AuthSchema = AuthSchema()
    endpoints: EndpointSchema = EndpointSchema()
