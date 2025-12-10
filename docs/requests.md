# Making API Requests

Client classes (`KeystoneClient` and `AsyncKeystoneClient`) provide a high-level interface for interacting the API.
This includes methods for generic HTTP requests in addition to resource-specific CRUD helpers for common workflows.
All requests automatically include any active authentication or session metadata.

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
Users are encouraged to familiarize themselves with the `httpx` library and it's methods for parsing response
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

Dedicated methods are provided for create, retrieve, update, and delete (CRUD) operations against each API resource.
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
