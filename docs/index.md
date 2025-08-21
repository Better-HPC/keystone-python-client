---
hide:
  - navigation
---

# Introduction

Keystone provides a Python client for streamlining interactions with the application's REST API.
The client automates user authentication and data parsing, freeing developers to focus on core application logic.

## Installation

The Python client is hosted on PyPI and can be installed in the standard fashion.

```bash
pip install keystone-api-client
```

## Instantiating a Client

The client package provides support for synchronous and asynchronous API calls.
In both cases, requests are pooled across a shared session, reducing HTTP overhead.
The following example instantiates a new session for a locally running server on port `8000`.
Creating the session with a context manager ensures open connections are automatically closed when no longer in use.

=== "Synchronous"

    ```python
    from keystone_client import KeystoneClient
    
    with KeystoneClient(url="http://localhost:8000") as client:
        ... # Your synchronous code here
    ```

=== "Asynchronous"

    ```python
    from keystone_client import AsyncKeystoneClient
    
    async with AsyncKeystoneClient(url="http://localhost:8000") as aclient:
        ... # Your asynchronous code here
    ```

Sessions can also be opened and closed manually.
This approach is generally discouraged as it increases the likelihood of resource leaks and unclosed connections.

=== "Synchronous"

    ```python
    from keystone_client import KeystoneClient
    
    client = KeystoneClient(url="http://localhost:8000"):
    # Your synchronous code here
    client.close()
    ```

=== "Asynchronous"

    ```python
    from keystone_client import AsyncKeystoneClient
    
    aclient = AsyncKeystoneClient(url="http://localhost:8000"):
    # Your asynchronous code here
    await aclient.close()
    ```

Client sessions will automatically manage any relevant session tokens.
This includes assigning a unique correlation ID (CID) used to track requests across Keystone application logs.
CID values are suitable for inclusion in log messages, passing to downstream services, or correlating requests
for debugging and performance monitoring.

=== "Synchronous"

    ```python
    from keystone_client import KeystoneClient
    
    with KeystoneClient(url="http://localhost:8000") as client:
        print(client.cid)
    ```

=== "Asynchronous"

    ```python
    from keystone_client import AsyncKeystoneClient
    
    async with AsyncKeystoneClient(url="http://localhost:8000") as aclient:
        print(aclient.cid)
    ```

## Authenticating a Session

The `login` and `logout` methods are used to handle user authentication.
Once authenticated, the client will automatically manage the resulting session tokens.

=== "Synchronous"

    ```python
    from keystone_client import KeystoneClient
    
    with KeystoneClient(url="http://localhost:8000") as client:
        client.login(username="username", password="password")
        assert client.is_authenticated()
        client.logout()
    ```

=== "Asynchronous"

    ```python
    from keystone_client import AsyncKeystoneClient
    
    async with AsyncKeystoneClient(url="http://localhost:8000") as aclient:
        await aclient.login(username="username", password="password")
        assert await aclient.is_authenticated()
        await aclient.logout()
    ```

## Generic HTTP Requests

Client classes provide dedicated methods for each HTTP request type supported by the API.
Any relevant session/authentication tokens are included automatically when submitting requests.

| HTTP Method | Function Name | Description                                              |
|-------------|---------------|----------------------------------------------------------|
| `GET`       | `http_get`    | Retrieve data from the server at the specified resource. |
| `POST`      | `http_post`   | Submit a new record to be processed by the server.       |
| `PUT`       | `http_put`    | Replace an existing record with a new one.               |
| `PATCH`     | `http_patch`  | Partially update an existing record.                     |
| `DELETE`    | `http_delete` | Remove the specified record from the server.             |

Request/response logic is handled using the `httpx` library.
API responses are returned as `httpx.Response` objects which encapsulate the response data and status code.
Users are encouraged to familiarize themselves with the `httpx.Response` object and it's methods for parsing response
data and related metadata.
A simple example is provided below.

=== "Synchronous"

    ```python
    from keystone_client import KeystoneClient
    
    with KeystoneClient(url="http://localhost:8000") as client:
        response = client.http_get('version')
        
    response.raise_for_status()
    print(response.status_code)
    print(response.content)
    ```

=== "Asynchronous"

    ```python
    from keystone_client import AsyncKeystoneClient
    
    async with AsyncKeystoneClient(url="http://localhost:8000") as aclient:
        response = await aclient.http_get('version')

    response.raise_for_status()
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
These methods accept record details as keyword arguments and return a dictionary with the successfully created record.

=== "Synchronous"

    ```python
    new_record_data = client.create_cluster(
        name="New-Cluster",
        description="Cluster created for example purposes."
    )
    ```

=== "Asynchronous"

    ```python
    new_record_data = await aclient.create_cluster(
        name="New-Cluster",
        description="Cluster created for example purposes."
    )
    ```

### Retrieving Records

Data retrieval methods are used to search and return existing records.
By default, these methods return all available records on the server as a list of dictionaries.
The `filters` argument can be used to optionally filter these values against a set of search parameters.
See the [filtering documentation](../../keystone-api/api/filtering/) for instructions on structuring search queries.

=== "Synchronous"

    ```python
    all_cluster_data = client.retrieve_cluster(filters={"name": "New-Cluster"})
    ```

=== "Asynchronous"

    ```python
    all_cluster_data = await aclient.retrieve_cluster(filters={"name": "New-Cluster"})
    ```

In situations where a record's primary key (i.e., it's `id` field) is already known, the individual record can be
retrieved directly.

=== "Synchronous"

    ```python
    single_cluster_data = client.retrieve_cluster(pk=1)
    ```

=== "Asynchronous"

    ```python
    single_cluster_data = await aclient.retrieve_cluster(pk=1)
    ```

### Updating Records

Update operations are used to modify values for an existing record.
Doing so requires specifying the record's primary key in addition to the new record values.

=== "Synchronous"

    ```python
    updated_record_data = client.update_cluster(
        pk=1,
        data={'description': "Updated description"}
    )
    ```

=== "Asynchronous"

    ```python
    updated_record_data = await aclient.update_cluster(
        pk=1,
        data={'description': "Updated description"}
    )
    ```

### Deleting Records

Delete methods are used to remove records from the server.

=== "Synchronous"

    ```python
    client.delete_cluster(pk=1)
    ```

=== "Asynchronous"

    ```python
    await aclient.delete_cluster(pk=1)
    ```

If a record does not exist for the provided primary key, the function call will exit silently.
The `raise_not_exists` argument can be used to raise an exception instead.

=== "Synchronous"

    ```python
    client.delete_cluster(pk=1, raise_not_exists=True)
    ```

=== "Asynchronous"

    ```python
    await aclient.delete_cluster(pk=1, raise_not_exists=True)
    ```

## Application Logging

API clients automatically log all requests with the Python logging framework. 
Log records are written to the `kclient` logger and include the application specific values listed below. 

| Field Name | Description                                                                          |
|------------|--------------------------------------------------------------------------------------|
| `cid`      | Logging identifier for the associated Keystone client session.                       |
| `baseurl`  | Base URL of the API server.                                                          |
| `method`   | HTTP request method, or an empty string if not applicable.                           |
| `endpoint` | API endpoint, or an empty string if not applicable.                                  |
| `url`      | Full API URL, including base URL and endpoint, or an empty string if not applicable. |


The `kclient` logger is automatically configured during import and context values are accessible in the
standard Python fashion.

```python
import logging
import keystone_client

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(cid)s - %(method)s - %(baseurl)s - %(endpoint)s - %(url)s - %(message)s')
)

log = logging.getLogger('kclient')
log.addHandler(handler)

log.info('Logging info')
```