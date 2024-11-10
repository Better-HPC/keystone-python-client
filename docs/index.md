---
hide:
  - navigation
---

# Introduction

Keystone provides a light-weight Python client for streamlining interactions with the application's REST API.
The client automatically manages user authentication and data parsing, freeing developers to focus on core application logic.

## Installation and Setup

The Python client is hosted on PyPI and can be installed in the standard fashion.

```bash
pip install keystone-api-client
```

## User Guide

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

### Creating Records

Create methods are used to submit new records to the API server.
These methods accept record details as keyword arguments and return a dictionary with the successfully created record data.

```python
new_record_data = client.create_cluster(
    name="New-Cluster",
    description="Cluster created for example purposes."
)
```

### Retrieving Records

Data retrieval methods are used to search and return existing records.
By default, these methods return all available records on the server as a list of dictionaries.
The `filters` argument can be used to optionally filter these values against a set of search parameters.
See the [filtering requests documentation](../../keystone-api/api/filtering/) for instructions on structuring search queries.

```python
all_cluster_data = client.retrieve_cluster(filters={"name": "New-Cluster"})
```

In situations where a record's primary key (i.e., it's `id` field) is already known, the individual record can be retrieved directly. 

```python
cluster_pk_one = client.retrieve_cluster(pk=1)
```

### Updating Records

Update operations are used to modify values for an existing record.
Doing so requires specifying the record's primary key in addition to the new record values.

```python
updated_record_data = client.update_cluster(
    pk=1,
    data={'description': "Updated description"}
)
```

### Deleting Records

Delete methods are used to removed records from the server.

```python
client.delete_cluster(pk=1)
```

If a record does not exist for the provided primary key, the function call will exit silently.
The `raise_not_exists` argument can be used to raise an exception instead.

```python
client.delete_cluster(pk=1, raise_not_exists=True)
```
