# Application Logging

The Keystone Python client exposes a dedicated logger (`kclient`) that records structured request metadata using the
standard Python logging framework. The logger is registered automatically when the package is imported and can be
configured like any other Python logger.

## Logger Configuration

Custom handlers, formatters, and filters may be attached directly to the kclient logger.
Because the logger behaves like any standard Python logger, you can control output destinations, define
message structures, adjust verbosity, and apply filtering based on logged metadata.

```python
import logging
import keystone_client

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
)

logging.getLogger('kclient').addHandler(handler)
```

In addition to the standard Python logging attributes, the `kclient` logger includes the following package-specific fields:

| Field Name | Description                                                                |
|------------|----------------------------------------------------------------------------|
| `cid`      | Per-session logging id used to correlate requests across a client session. |
| `baseurl`  | Base API server URL, including http protocol.                              |
| `method`   | HTTP method for outgoing requests, or an empty string if not applicable.   |
| `endpoint` | API endpoint for outgoing requests, or an empty string if not applicable.  |
| `url`      | Full API URL for outgoing requests, or an empty string if not applicable.  |

## Session IDs

Each client session is assigned a unique correlation ID (CID) that accompanies all emitted log records.
This identifier provides a reference value for correlating client and API logs across multiple endpoints and requests.
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
