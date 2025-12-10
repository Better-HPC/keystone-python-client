# Install and Setup

The Keystone platform includes an official Python client that simplifies integration with the application's REST API.
It handles authentication, request execution, and response parsing, allowing developers to concentrate on application
logic rather than API mechanics.

The client is published on PyPI and can be installed in the standard fashion.

```bash
pip install keystone-api-client
```

!!! note "Version Compatibility"

    The API client version should match the major and minor version of the upstream API server.
    For example, if the API version is `2.3.x`, the compatible client version is `2.3.y`.
    Using a mismatched client version may still function, but compatibility is not guaranteed and may
    result in inconsistent behavior.
