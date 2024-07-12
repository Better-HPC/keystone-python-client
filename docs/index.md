---
hide:
  - navigation
---

# Python Client

Keystone provides a light-weight Python client designed to streamline interactions with the Keystone API.
The client automatically manages user authentication and data parsing, making it easier for developers to build against
the Keystone framework.

## Installation and Setup

The Python client is hosted on PyPI and can be installed in the standard fashion.

```bash
pip install keystone-api-client
```

## Client Authentication

The `KeystoneClient` class encapsulates user authentication and API requests.
Create a new instance by providing the URL of the running API server you want to interact with.
In the following example, a client instance is create for a local server instance.

```python
from keystone_client import KeystoneClient

client = KeystoneClient(url="http://localhost:8000")
```

The `login` method is used to authenticate against the API server.

```python
client.login(username="username", password="password")
```

The client will cache the resulting JWT tokens are then cached in memory.
Similarly, the `logout` method will clear any cached credentials and ask the API to blacklist the current refresh token.

```python
client.logout()
```

## Submitting API Requests

### CRUD Methods

### Generic HTTP Requests

For developers looking to make generic HTTP requests, the client provides dedicated methods.

| HTTP Method | Client Method |
|-------------|---------------|
| `GET`       | `http_get`    |
| `POST`      | `http_post`   |
| `PUT`       | `http_put`    |
| `DELETE`    | `http_delete` |
| `PATCH`     | `http_patch`  |
