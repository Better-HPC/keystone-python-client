from typing import Literal

from httpx._types import QueryParamTypes, RequestContent, RequestData, RequestFiles

__all__ = [
    'HTTP_METHOD',
    'QueryParamTypes',
    'RequestContent',
    'RequestData',
    'RequestFiles',
]

HTTP_METHOD = Literal["get", "post", "put", "patch", "delete"]
