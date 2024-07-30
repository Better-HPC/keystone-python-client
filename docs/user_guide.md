# User Guide

The `KeystoneClient` class is used to encapsulate user authentication and API requests.
New instances are created by specifying the API URL.
In the following example, a client instance is defined for a locally running server on port `8000`.

```python
from keystone_client import KeystoneClient

client = KeystoneClient(url="http://localhost:8000")  # (1)!
```

1. Specifying a network protocol is required when instantiating new instances (e.g., `http://` or `https://`).

The `login` and `logout` methods are used to handle user authentication.
Once authenticated, the client will automatically manage the resulting user credentials, including refreshing JWT
tokens.

```python
client.login(username="username", password="password")  # (1)!
assert client.is_authenticated  # (2)!
client.logout()  # (3)!
```

1. Authenticate a new user session.
2. Check the authentication status at any time.
3. End the authenticated session and blacklist current credentials.

## Generic HTTP Requests

The client provides dedicated methods for each HTTP request type supported by the API.
When authenticated, the client will automatically include the appropriate authentication headers when submitting
requests.

| HTTP Method | Function Name | Description                                              |
|-------------|---------------|----------------------------------------------------------|
| `GET`       | `http_get`    | Retrieve data from the server at the specified resource. |
| `POST`      | `http_post`   | Submit a new record to be processed by the server.       |
| `PUT`       | `http_put`    | Replace an existing record with a new one.               |
| `PATCH`     | `http_patch`  | Partially update an existing record.                     |
| `DELETE`    | `http_delete` | Remove the specified record from the server.             |

Request/response logic is handled using the popular `requests` library.
API responses are returned as `requests.Response` objects encapsulating the response data and status code.

```python
response = client.http_get('version')

print(response.status_code)
print(response.content)
```

## CRUD Operations

Dedicated methods are provided for create, retrieve, update, and delete (CRUD) operations for each API resource.
These methods simplify data manipulation by automatically handling the request and response logic.

CRUD methods adhere to the following naming scheme:

| Method Name           | Description                                              |
|-----------------------|----------------------------------------------------------|
| `create_{resource}`   | Create a new record for the specified resource.          |
| `retrieve_{resource}` | Retrieve one or more records for the specified resource. |
| `update_{resource}`   | Update an existing record for the specified resource.    |
| `delete_{resource}`   | Delete an existing record for the specified resource.    |

The following example demonstrates how to use the CRUD methods:

```python
# Create a new record
new_cluster = client.create_cluster(
    name="New-Cluster",
    description="Cluster created for example purposes."
)

# Retrieve a single record by primary key
cluster = client.retrieve_cluster(pk=1)

# Retrieve multiple records with filters
clusters = client.retrieve_cluster(filters={"name": "New-Cluster"})

# Update an existing record
updated_cluster = client.update_cluster(
    pk=1,
    data={'description': "Updated description"}
)

# Delete an existing record
client.delete_cluster(pk=1)
```
