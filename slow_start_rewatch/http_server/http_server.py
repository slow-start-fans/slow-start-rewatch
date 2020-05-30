# -*- coding: utf-8 -*-

import threading

import requests
from flask import Flask, render_template, request, url_for
from structlog import get_logger
from werkzeug.exceptions import HTTPException
from werkzeug.serving import run_simple

from slow_start_rewatch.exceptions import AuthorizationError

log = get_logger()

app = Flask(__name__)

REDDIT_ACCESS_DENIED = "access_denied"
INVALID_STATE_ERROR = "invalid_state"
INVALID_REQUEST_ERROR = "invalid_request"
AUTO_SHUTDOWN_DELAY = 2.0


def run(state: str, hostname: str, port: int, auto_shutdown=True) -> str:
    """
    Run the HTTP server.

    The server can be stopped by calling :func:`request_shutdown()` or by
    sending POST request to ``/shutdown`` path.
    """
    log.info("http_server_run", hostname=hostname, port=port, state=state)
    app.config["INITIAL_STATE"] = state
    app.config["RETRIEVED_CODE"] = None
    app.config["AUTHORIZATION_ERROR"] = None
    app.config["SERVER_NAME"] = "{0}:{1}".format(hostname, port)
    app.config["AUTO_SHUTDOWN"] = auto_shutdown
    app.config["SHUTTING_DOWN"] = False

    run_simple(hostname, port, app)

    error = app.config["AUTHORIZATION_ERROR"]
    code = app.config["RETRIEVED_CODE"]

    log.info("http_server_stopped", code=code, error=error)

    if not code and not error:
        error = "The authorization has been interrupted."

    if error:
        log.error("oauth_authorize_failed", error=error)
        raise AuthorizationError(error)

    return code


def request_shutdown() -> None:
    """Send the shutdown request to the server."""
    log.info("server_shutdown_request_send")

    with app.app_context():  # type: ignore
        requests.post(url_for("shutdown"))


@app.route("/shutdown", methods=["POST"])
def shutdown():
    """Initiate the Werkzeug server shutdown."""
    log.info("server_shutdown_request_received")

    server_shutdown = request.environ.get("werkzeug.server.shutdown")
    server_shutdown()  # type: ignore

    return "Server shutting down..."


@app.teardown_request
def teardown_request(exception=None):
    """Dispatche the server shutdown request."""
    if app.config["SHUTTING_DOWN"] or not app.config["AUTO_SHUTDOWN"]:
        return

    app.config["SHUTTING_DOWN"] = True

    log.info("server_shutdown_request_schedule", delay=AUTO_SHUTDOWN_DELAY)
    timer = threading.Timer(AUTO_SHUTDOWN_DELAY, request_shutdown)
    timer.start()


def auth_error(error_name: str):
    """Render a view with an error message."""
    template = "authorization_error.html"

    if error_name == REDDIT_ACCESS_DENIED:
        template = "access_denied.html"
        error_message = "The access to Reddit was denied."
    elif error_name == INVALID_STATE_ERROR:
        error_message = "Invalid state."
    elif error_name == INVALID_REQUEST_ERROR:
        error_message = (
            "This page is not meant to be opened before " +
            "completing authorization on Reddit."
        )
    else:
        error_message = "Reddit API error: {0}".format(error_name)

    app.config["AUTHORIZATION_ERROR"] = error_message

    log.info("server_response", template=template, error_message=error_message)
    return render_template(template, error_message=error_message)


@app.route("/", methods=["GET"])
def index():
    """Render the index page."""
    state = request.args.get("state")
    code = request.args.get("code")
    error = request.args.get("error")

    log.info("server_request", state=state, code=code, error=error)

    if error:
        return auth_error(error)

    if not code:
        return auth_error(INVALID_REQUEST_ERROR)

    if state != app.config["INITIAL_STATE"]:
        return auth_error(INVALID_STATE_ERROR)

    app.config["RETRIEVED_CODE"] = code

    template = "success.html"
    log.info("server_response", template=template)
    return render_template(template)


@app.errorhandler(HTTPException)
def handle_exception(error):
    """Render the HTTP error page."""
    template = "http_error.html"
    log.info("server_response", error=error)
    return render_template(
        template,
        error_code=error.code,
        error_name=error.name,
        error_description=error.description,
    ), error.code
