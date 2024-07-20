from typing import Tuple

from pydantic import BaseModel


class AuthSchema(BaseModel):
    new: str = "authentication/new/"
    refresh: str = "authentication/refresh/"
    blacklist: str = "authentication/blacklist/"


class Schema(BaseModel):
    auth: AuthSchema = AuthSchema()
    endpoints: Tuple[str, ...] = (
        "allocations",
        "requests",
        "research_groups",
        "users",
    )
