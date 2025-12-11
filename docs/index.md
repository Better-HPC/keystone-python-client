# Keystone Python Client

The Keystone platform includes an official Python client that simplifies integration with the application's REST API.
It handles authentication, request execution, and response parsing, allowing developers to concentrate on application
logic rather than API mechanics.

The client is published on the BHPC package registry and can be installed in the standard fashion.

```sh
BHPC_REPO="https://dl.cloudsmith.io/public/better-hpc/keystone/python/simple/"
pip install --extra-index-url=$BHPC_REPO keystone-api-client
```

!!! danger "Version Compatibility"

    The API client version should match the major and minor version of the upstream API server.
    For example, if the API version is `2.3.x`, the compatible client version is `2.3.y`.
    Using a mismatched client version may still function, but compatibility is not guaranteed and may
    result in inconsistent behavior.
