# -*- coding: utf-8 -*-

import threading
from concurrent import futures

import pytest
import requests
from werkzeug.exceptions import MethodNotAllowed, NotFound

from slow_start_rewatch.http_server import http_server
from tests.conftest import HTTP_SERVER_HOSTNAME, HTTP_SERVER_PORT, OAUTH_CODE


@pytest.mark.parametrize(("query_string", "title", "gif"), [
    pytest.param(
        "?state=blushing&code=anime_girls_are_cute",
        "Welcome",
        "success.gif",
        id="success",
    ),
    pytest.param(
        "",
        "not meant to be opened",
        "authorization-error.gif",
        id="invalid_request",
    ),
    pytest.param(
        "?state=invalid_state&code=anime_girls_are_cute",
        "Invalid state",
        "authorization-error.gif",
        id="invalid_state",
    ),
    pytest.param(
        "?code=anime_girls_are_cute",
        "Invalid state",
        "authorization-error.gif",
        id="missing_state",
    ),
    pytest.param(
        "?state=blushing&error=test_error",
        "test_error",
        "authorization-error.gif",
        id="auth_error",
    ),
    pytest.param(
        "?state=blushing&error=access_denied",
        "Access Denied",
        "access-denied.gif",
        id="access_denied",
    ),
])
def test_response(server_url, query_string, title, gif):
    """Test responses based on query strings."""
    url = "{0}/{1}".format(server_url, query_string)
    response = requests.get(url)

    assert response.ok
    assert title in response.text
    assert gif in response.text


@pytest.mark.parametrize(("path", "error_code", "title", "gif"), [
    pytest.param(
        "not-cute-enough/",
        NotFound.code,
        "Not Found",
        "http-error.gif",
        id="not_found",
    ),
    pytest.param(
        "shutdown",
        MethodNotAllowed.code,
        "Method Not Allowed",
        "http-error.gif",
        id="not_found",
    ),
])
def test_http_error(server_url, path, error_code, title, gif):
    """Test error pages."""
    url = "{0}/{1}".format(server_url, path)
    response = requests.get(url)

    assert response.status_code == error_code
    assert title in response.text
    assert gif in response.text


def test_run(server_run_future):
    """Test server run and retrieving the auth code."""
    base_url = "http://{0}:{1}".format(HTTP_SERVER_HOSTNAME, HTTP_SERVER_PORT)
    url = "{0}/?state=blushing&code=anime_girls_are_cute".format(base_url)

    response = requests.get(url)
    code = server_run_future.result(timeout=10)

    assert response.ok
    assert code == OAUTH_CODE

    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(url, timeout=1)


@pytest.fixture()
def server_url():
    """
    Create server instance in a separate thread.

    Yield base URL of the server and shut down the server after the test.
    """
    base_url = "http://{0}:{1}".format(HTTP_SERVER_HOSTNAME, HTTP_SERVER_PORT)

    thread = threading.Thread(
        target=http_server.run,
        kwargs={
            "state": "blushing",
            "hostname": HTTP_SERVER_HOSTNAME,
            "port": HTTP_SERVER_PORT,
            "auto_shutdown": False,
        },
    )

    thread.start()
    try:
        yield base_url
    finally:
        http_server.request_shutdown()
        thread.join(timeout=5.0)


@pytest.fixture()
def server_run_future():
    """
    Return :class:`asyncio.Future` encapsulating :meth:`http_server.run()`.

    The return value is retrieved by calling :meth:`future.result()`.
    """
    with futures.ThreadPoolExecutor() as executor:
        future = executor.submit(
            http_server.run,
            state="blushing",
            hostname=HTTP_SERVER_HOSTNAME,
            port=HTTP_SERVER_PORT,
            auto_shutdown=True,
        )
        yield future
