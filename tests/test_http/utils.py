"""Utility functions for common testing setup/execution tasks."""

import httpx


def test_request_handler(request: httpx.Request) -> httpx.Response:
    """HTTP request handler that returns metadata about the incoming request."""

    return httpx.Response(
        status_code=200,
        json={
            'url': str(request.url),
            'method': request.method,
            'headers': dict(request.headers),
            'params': request.url.params.multi_items(),
        },
    )
