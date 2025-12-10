# Application Logging

API clients automatically log all requests to the `kclient` log handler.
In addition to the standard default values, `kclient` logs include the application specific values listed below.

| Field Name | Description                                                                |
|------------|----------------------------------------------------------------------------|
| `cid`      | Per-session logging id used to correlate requests across a client session. |
| `baseurl`  | Base API server URL, including http protocol.                              |
| `method`   | HTTP method for outgoing requests, or an empty string if not applicable.   |
| `endpoint` | API endpoint for outgoing requestst, or an empty string if not applicable. |
| `url`      | Full API URL for outgoing requests, or an empty string if not applicable.  |

The `kclient` logger is automatically registered when importing the `keystone_client` package.
Formatting, filtering, and persisting log values is left to the user.
For example:

```python
import logging
import keystone_client

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(cid)s - %(baseurl)s - %(method)s - %(endpoint)s - %(message)s')
)

logging.getLogger('kclient').addHandler(handler)
```
