# -*- coding: utf-8 -*-

import pytest

from xTool import exceptions
from bs4 import BeautifulSoup

from xTool.apps.sanic import Sanic
from xTool.exceptions import (
    Forbidden,
    InvalidUsage,
    NotFound,
    ServerError,
    Unauthorized,
    abort,
)
from xTool.response import text


class SanicExceptionTestException(Exception):
    pass


@pytest.fixture(scope="module")
def exception_app():
    app = Sanic("test_exceptions")

    @app.route("/")
    def handler(request):
        return text("OK")

    @app.route("/error")
    def handler_error(request):
        raise ServerError("OK")

    @app.route("/404")
    def handler_404(request):
        raise NotFound("OK")

    @app.route("/403")
    def handler_403(request):
        raise Forbidden("Forbidden")

    @app.route("/401")
    def handler_401(request):
        raise Unauthorized("Unauthorized")

    @app.route("/401/basic")
    def handler_401_basic(request):
        raise Unauthorized("Unauthorized", scheme="Basic", realm="Sanic")

    @app.route("/401/digest")
    def handler_401_digest(request):
        raise Unauthorized(
            "Unauthorized",
            scheme="Digest",
            realm="Sanic",
            qop="auth, auth-int",
            algorithm="MD5",
            nonce="abcdef",
            opaque="zyxwvu",
        )

    @app.route("/401/bearer")
    def handler_401_bearer(request):
        raise Unauthorized("Unauthorized", scheme="Bearer")

    @app.route("/invalid")
    def handler_invalid(request):
        raise InvalidUsage("OK")

    @app.route("/abort/401")
    def handler_401_error(request):
        abort(401)

    @app.route("/abort")
    def handler_500_error(request):
        abort(500)
        return text("OK")

    @app.route("/abort/message")
    def handler_abort_message(request):
        abort(500, message="Abort")

    @app.route("/divide_by_zero")
    def handle_unhandled_exception(request):
        _ = 1 / 0

    @app.route("/error_in_error_handler_handler")
    def custom_error_handler(request):
        raise SanicExceptionTestException("Dummy message!")

    @app.exception(SanicExceptionTestException)
    def error_in_error_handler_handler(request, exception):
        _ = 1 / 0

    return app


def test_XToolConfigException():
    with pytest.raises(exceptions.XToolConfigException) as excinfo:
        raise exceptions.XToolConfigException


def test_XToolSensorTimeout():
    with pytest.raises(exceptions.XToolSensorTimeout) as excinfo:
        raise exceptions.XToolSensorTimeout


def test_XToolTaskTimeout():
    with pytest.raises(exceptions.XToolTaskTimeout) as excinfo:
        raise exceptions.XToolTaskTimeout


def test_XToolWebServerTimeout():
    with pytest.raises(exceptions.XToolWebServerTimeout) as excinfo:
        raise exceptions.XToolWebServerTimeout


def test_XToolSkipException():
    with pytest.raises(exceptions.XToolSkipException) as excinfo:
        raise exceptions.XToolSkipException


def test_XToolDagCycleException():
    with pytest.raises(exceptions.XToolDagCycleException) as excinfo:
        raise exceptions.XToolDagCycleException
