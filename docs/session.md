# Starting a Session

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
