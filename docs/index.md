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

The KeystoneClient class includes dedicated methods for create, retrieve, update, and delete (CRUD) operations for each API endpoint. 
These methods simplify data manipulation by handling the request and response logic internally.

The following CRUD methods are available for interacting with the API endpoints:

| Method Name           | Description                                              |
|-----------------------|----------------------------------------------------------|
| `create_{resource}`   | Create a new record for the specified resource.          |
| `retrieve_{resource}` | Retrieve one or more records for the specified resource. |
| `update_{resource}`   | Update an existing record for the specified resource.    |
| `delete_{resource}`   | Delete an existing record for the specified resource.    |

Below are examples demonstrating how to use the CRUD methods:

```python
# Create a new allocation record
new_allocation = client.create_allocation(
    name="New Allocation",
    description="Description for new allocation"
)

# Retrieve an allocation record by primary key
allocation = client.retrieve_allocation(pk=1)

# Retrieve multiple allocation records with filters
allocations = client.retrieve_allocation(filters={"status": "active"})

# Update an existing allocation record
updated_allocation = client.update_allocation(
    pk=1,
    name="Updated Allocation",
    description="Updated description"
)

# Delete an allocation record
client.delete_allocation(pk=1)
```

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
