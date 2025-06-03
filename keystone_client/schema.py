"""Schema objects used to define available API endpoints."""

import json
from pathlib import Path
from typing import NamedTuple

import yaml


class Endpoint(NamedTuple):
    """API endpoint metadata."""

    path: str
    method: str
    operation_id: str


class Schema:
    """Parses an OpenAPI specification file to extract HTTP operation metadata."""

    def __init__(self, spec_path: str | Path) -> None:
        """Load API endpoints from an OpenAPI spec file.

        Args:
            spec_path: Path to the OpenAPI file.
        """

        spec_path = Path(spec_path)
        file_data = self._load_openapi_spec(spec_path)
        self._endpoints = self._extract_endpoints(file_data)

    @property
    def endpoints(self) -> list[Endpoint]:
        return self._endpoints.copy()

    def _load_openapi_spec(self, file_path: Path) -> dict:
        """Parse an OpenAPI file and return its contents.

        Supports Yaml and Json file formats.

        Args:
            file_path: Path to the OpenAPI file.

        Returns:
            A dictionary containing the OpenApi specification data.
        """

        with file_path.open() as in_file:
            if file_path.suffix in ('.yaml', '.yml'):
                return yaml.safe_load(in_file)

            elif file_path.suffix == '.json':
                return json.load(in_file)

            raise ValueError("Unsupported OpenAPi file format. Use .json or .yaml/.yml")

    def _extract_endpoints(self, openapi_spec: dict) -> list[Endpoint]:
        """Extract endpoint definitions from the OpenAPI spec."""

        endpoints: list[Endpoint] = []
        paths = openapi_spec.get("paths", {})

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() in {"get", "post", "put", "patch", "delete"}:
                    operation_id = operation.get("operationId")
                    endpoints.append(Endpoint(method.upper(), path, operation_id))

        return endpoints
