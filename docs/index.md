# Introduction

Keystone provides a Python client for streamlining interactions with the application's REST API.
The client automates user authentication and data parsing, freeing developers to focus on their core application logic.

The Python client is hosted on PyPI and can be installed in the standard fashion.

```bash
pip install keystone-api-client
```

!!! note "Version Compatibility"

    The API client version should match the major and minor version of the upstream API server.
    For example, if the API version is `2.3.x`, the compatible client version is `2.3.y`.
    Using a mismatched client version may still function, but compatibility is not guaranteed and may
    result in inconsistent behavior.
