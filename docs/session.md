# Starting a Session

Interacting with the Keystone API begins by creating a client session. 
<<<<<<< Updated upstream
Session objects encapsulate the connection state and request configuration, allowing the
client to efficiently reuse connections and manage resources across multiple API calls.
=======
Session objects encapsulate the connection state, authentication details, and request configuration, allowing the
client to efficiently reuse connections across multiple API calls.
>>>>>>> Stashed changes

## Instantiating a Client

The client package provides support for synchronous and asynchronous API calls.
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
