# Application Logging

The `kclient` Python logger is automatically registered on package import. 
It provides full compatibility with the standard Python `logging` module and can be accessed and customized in the 
standard fashion.

```python
import logging
import keystone_client

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
)

logging.getLogger('kclient').addHandler(handler)
```

## Custom Logging Fields

In addition to Python's built-in message fields, the `kclient` logger also exposes the following package-specific values.
These fields are passed to all log messages and may be accessed via custom formatters or filters.

| Field Name | Description                                                                |
|------------|----------------------------------------------------------------------------|
| `cid`      | Per-session logging id used to correlate requests across a client session. |
| `baseurl`  | Base API server URL, including http protocol.                              |
| `method`   | HTTP method for outgoing requests, or an empty string if not applicable.   |
| `endpoint` | API endpoint for outgoing requests, or an empty string if not applicable.  |
| `url`      | Full API URL for outgoing requests, or an empty string if not applicable.  |

## Session IDs

Each client session is assigned a unique correlation ID (CID) that accompanies all emitted log records.
CID values are accessible as logging fields or directly from an active client session, demonstrated below:

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
