# Getting Started

The `KeystoneClient` and `AsyncKeystoneClient` classes offer a streamlined, session-based interface for interacting with
the Keystone API. They automatically manage common connection settings to ensure requests are submitted efficiently
and abstract away low level API mechanics so developers can focus on application logic.

## Instantiating a Client

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

Sessions can also be opened and closed manually, although this approach is generally discouraged as it increases
the likelihood of resource leaks and unclosed connections.

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

## Making API Requests

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
