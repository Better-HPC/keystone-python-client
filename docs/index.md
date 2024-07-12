---
hide:
  - navigation
---

# API Client

Keystone provides a light-weight Python client for streamlining interactions with the Keystone API.
The client automatically manages user authentication and data parsing, making it easier for developers to build against
the Keystone framework.

## Installation and Setup

The Python client is hosted on PyPI and can be installed in the standard fashion.

```bash
pip install keystone-api-client
```

## Client Authentication

The `KeystoneClient` class is used to encapsulate user authentication and API requests.
New instances are created by specifying the API server you want to interact with.
In the following example, a client instance is defined for a locally running server on port `8000`.

```python
from keystone_client import KeystoneClient

client = KeystoneClient(url="http://localhost:8000")
```

The `login` and `logout` methods are used to handle authentication against the API server.

```python
# Authenticate a new user session
client.login(username="username", password="password")

# Check the authentication status at any time
assert client.is_authenticated

# End the authenticated session
client.logout()
```

The client will cache any JWT tokens in memory and automatically refresh them as necessary.
No mechanism is provided to manually manage cached credentials.

## Submitting API Requests

The API client provides two groups of methods for submitting requests.

### CRUD Methods

Dedicate methods are provided for create, retrieve, update, and delete (CRUD) operations against each API endpoint.

!!! warning "Work in Progress"

    Methods for performing CRUD operations are till under development.
    Formal documentation is unavailable at this time.

### Generic HTTP Requests

For developers looking to make generic HTTP requests, the client provides dedicated methods for each HTTP request type.
If authenticated, the client will automatically include the appropriate authentication headers when submitting new requests.

| HTTP Method | Function Name |
|-------------|---------------|
| `GET`       | `http_get`    | 
| `POST`      | `http_post`   |
| `PUT`       | `http_put`    |
| `DELETE`    | `http_delete` |
| `PATCH`     | `http_patch`  |

Request/response logic is handled using the popular `requests` library.
Each HTTP method returns a `requests.Response` object encapsulating the data and status code returned by the server.

```python
response = client.http_get('version')

print(response.status_code)
print(response.content)
```
