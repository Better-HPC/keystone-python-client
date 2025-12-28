# Keystone Python Client

Keystone includes an official Python client designed to simplify integration with the platform's [REST API](../keystone-api).
It handles authentication, request execution, and response parsing, allowing developers to concentrate on application
logic rather than API mechanics.

The client is published on the BHPC package registry and can be installed using the `pip` package manager:

```sh
BHPC_REPO="https://dl.cloudsmith.io/public/better-hpc/keystone/python/simple/"
pip install --extra-index-url=$BHPC_REPO keystone-api-client
```
