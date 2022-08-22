# -*- coding: utf-8 -*-

from enum import Enum, unique, IntEnum

from xTool.status import STATUS_CODES

_http_status_exceptions = {}


def add_status_code(code, quiet=None):
    """类装饰器，用于给类添加状态码
    Decorator used for adding exceptions to :class:`HttpStatusException`.
    """

    def class_decorator(cls):
        cls.status_code = code
        if quiet or quiet is None and code != 500:
            cls.quiet = True
        _http_status_exceptions[code] = cls
        return cls

    return class_decorator


class HttpStatusException(Exception):

    def __init__(self, message, status_code=None, quiet=None):
        super().__init__(message)

        if status_code is not None:
            self.status_code = status_code

        # quiet=None/False/True with None meaning choose by status
        if quiet or quiet is None and status_code not in (None, 500):
            self.quiet = True


@add_status_code(404)
class NotFound(HttpStatusException):
    pass


@add_status_code(400)
class InvalidUsage(HttpStatusException):
    pass


@add_status_code(405)
class MethodNotSupported(HttpStatusException):

    def __init__(self, message, _, allowed_methods):
        super().__init__(message)
        self.headers = {"Allow": ", ".join(allowed_methods)}


@add_status_code(500)
class ServerError(HttpStatusException):
    pass


@add_status_code(503)
class ServiceUnavailable(HttpStatusException):
    """The server is currently unavailable (because it is overloaded or
    down for maintenance). Generally, this is a temporary state."""

    pass


class URLBuildError(ServerError):
    pass


class FileNotFound(NotFound):

    def __init__(self, message, path, relative_url):
        super().__init__(message)
        self.path = path
        self.relative_url = relative_url


@add_status_code(408)
class RequestTimeout(HttpStatusException):
    """The Web server (running the Web site) thinks that there has been too
    long an interval of time between 1) the establishment of an IP
    connection (socket) between the client and the server and
    2) the receipt of any data on that socket, so the server has dropped
    the connection. The socket connection has actually been lost - the Web
    server has 'timed out' on that particular socket connection.
    """

    pass


@add_status_code(413)
class PayloadTooLarge(HttpStatusException):
    pass


class HeaderNotFound(InvalidUsage):
    pass


@add_status_code(416)
class ContentRangeError(HttpStatusException):

    def __init__(self, message, content_range):
        super().__init__(message)
        self.headers = {"Content-Range": f"bytes */{content_range.total}"}


@add_status_code(417)
class HeaderExpectationFailed(HttpStatusException):
    pass


@add_status_code(403)
class Forbidden(HttpStatusException):
    pass


class InvalidRangeType(ContentRangeError):
    pass


class PyFileError(Exception):

    def __init__(self, file):
        super().__init__("could not execute config file %s", file)


@add_status_code(401)
class Unauthorized(HttpStatusException):
    """
    Unauthorized exception (401 HTTP status code).

    :param message: Message describing the exception.
    :param status_code: HTTP Status code.
    :param scheme: Name of the authentication scheme to be used.

    When present, kwargs is used to complete the WWW-Authentication header.

    Examples::

        # With a Basic auth-scheme, realm MUST be present:
        raise Unauthorized("Auth required.",
                           scheme="Basic",
                           realm="Restricted Area")

        # With a Digest auth-scheme, things are a bit more complicated:
        raise Unauthorized("Auth required.",
                           scheme="Digest",
                           realm="Restricted Area",
                           qop="auth, auth-int",
                           algorithm="MD5",
                           nonce="abcdef",
                           opaque="zyxwvu")

        # With a Bearer auth-scheme, realm is optional so you can write:
        raise Unauthorized("Auth required.", scheme="Bearer")

        # or, if you want to specify the realm:
        raise Unauthorized("Auth required.",
                           scheme="Bearer",
                           realm="Restricted Area")
    """

    def __init__(self, message, status_code=None, scheme=None, **kwargs):
        super().__init__(message, status_code)

        # if auth-scheme is specified, set "WWW-Authenticate" header
        if scheme is not None:
            values = ['{!s}="{!s}"'.format(k, v) for k, v in kwargs.items()]
            challenge = ", ".join(values)

            self.headers = {
                "WWW-Authenticate": f"{scheme} {challenge}".rstrip()
            }


def abort(status_code, message=None):
    """
    Raise an exception based on HttpStatusException. Returns the HTTP response
    message appropriate for the given status code, unless provided.

    :param status_code: The HTTP status code to return.
    :param message: The HTTP response body. Defaults to the messages
                    in response.py for the given status code.
    """
    if message is None:
        message = STATUS_CODES.get(status_code)
        # These are stored as bytes in the STATUS_CODES dict
        message = message.decode("utf8")
    http_status_exception = _http_status_exceptions.get(
        status_code, HttpStatusException)
    raise http_status_exception(message=message, status_code=status_code)


class AirflowException(Exception):
    """
    Base class for all Airflow's errors.
    Each custom exception should be derived from this class
    """

    status_code = 500


class AirflowBadRequest(AirflowException):
    """Raise when the application or server cannot handle the request"""

    status_code = 400


class AirflowNotFoundException(AirflowException):
    """Raise when the requested object/resource is not available in the system"""

    status_code = 404


class AirflowConfigException(AirflowException):
    pass


class AirflowSensorTimeout(AirflowException):
    pass


class AirflowTaskTimeout(AirflowException):
    pass


class AirflowWebServerTimeout(AirflowException):
    pass


class AirflowSkipException(AirflowException):
    pass


class AirflowDagCycleException(AirflowException):
    pass


class AirflowPluginException(AirflowException):
    pass


class XToolException(AirflowException):
    """
    Base class for all Airflow's errors.
    Each custom exception should be derived from this class
    """

    status_code = 500
    code = -1
    message = "系统异常，请联系管理员"
    message_template = "系统异常，请联系管理员"

    def __init__(self, data=None, extra=None, **kwargs) -> None:
        self.data = data
        self.extra = extra if extra else {}
        if kwargs:
            try:
                self.message = self.message_template.format(**kwargs)
            except Exception:  # noqa
                pass

    def __str__(self) -> str:
        return str(self.message)


class XToolBadRequest(XToolException):
    """Raise when the application or server cannot handle the request"""

    status_code = 400


class XToolNotFoundException(XToolException):
    """Raise when the requested object/resource is not available in the system"""

    status_code = 404


class XToolConfigException(XToolException, AirflowConfigException):
    pass


class XToolSensorTimeout(XToolException):
    pass


class XToolTaskTimeout(XToolException, AirflowTaskTimeout):
    pass


class XToolWebServerTimeout(XToolException):
    pass


class XToolSkipException(XToolException):
    pass


class XToolDagCycleException(XToolException):
    pass


class XToolPluginException(XToolException, AirflowPluginException):
    pass


class DagNotFound(XToolNotFoundException):
    """Raise when a DAG is not available in the system"""

    pass


class DagRunNotFound(XToolNotFoundException):
    """Raise when a DAG Run is not available in the system"""

    pass


class DagRunAlreadyExists(XToolBadRequest):
    """Raise when creating a DAG run for DAG which already has DAG run entry"""

    pass


class DagFileExists(XToolBadRequest):
    """Raise when a DAG ID is still in DagBag i.e., DAG file is in DAG folder"""

    pass


class TaskNotFound(XToolNotFoundException):
    """Raise when a Task is not available in the system"""

    pass


class TaskInstanceNotFound(XToolNotFoundException):
    """Raise when a Task Instance is not available in the system"""

    pass


class PoolNotFound(XToolNotFoundException):
    """Raise when a Pool is not available in the system"""

    pass


class PortInvalidError(XToolException):
    pass


class InvalidStatsNameException(XToolException):
    """Raise when name of the stats is invalid"""


class XToolTimeoutError(AssertionError):
    """Thrown when a timeout occurs in the `timeout` context manager."""

    def __init__(self, value="Timed Out"):
        self.value = value

    def __str__(self):
        return repr(self.value)


@unique
class ErrorType(IntEnum):
    SDKError = 1


@unique
class ErrorCode(IntEnum):
    """错误码类型 ."""

    # 成功
    ERR_OK = 0
    ERR_UNKNOWN = -1


@unique
class ErrMessage(Enum):
    ERR_UNKNOWN = "Unkown error"
    ERR_OK = "OK"


class BaseErrorException(Exception):

    def __init__(self, exception_type: ErrorType, code: ErrorCode,
                 message: str):
        self.type = exception_type
        self.code = code
        self.message = str(message)


class SDKError(BaseErrorException):

    def __init__(self, code: ErrorCode, message: str):
        super().__init__(ErrorType.SDKError, code, message)


def new_sdk_error(code: ErrorCode, message: str):
    return SDKError(code, message)
