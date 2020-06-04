# -*- coding: utf-8 -*-

from traceback import format_exc

from xTool.errorpages import exception_response
from xTool.exceptions import (
    ContentRangeError,
    HeaderNotFound,
    InvalidRangeType,
)
from xTool.log.log import logger
from xTool.response import text


class ErrorHandler:
    """
    Provide :class:`sanic.app.Sanic` application with a mechanism to handle
    and process any and all uncaught exceptions in a way the application
    developer will set fit.

    This error handling framework is built into the core that can be extended
    by the developers to perform a wide range of tasks from recording the error
    stats to reporting them to an external service that can be used for
    realtime alerting system.

    """

    handlers = None
    cached_handlers = None
    _missing = object()

    def __init__(self):
        # 存放注册的异常和错误处理器的映射关系
        self.handlers = []
        self.cached_handlers = {}
        self.debug = False

    def add(self, exception, handler):
        """添加错误处理器
        Add a new exception handler to an already existing handler object.

        :param exception: Type of exception that need to be handled
        :param handler: Reference to the method that will handle the exception

        :type exception: :class:`sanic.exceptions.SanicException` or
            :class:`Exception`
        :type handler: ``function``

        :return: None
        """
        self.handlers.append((exception, handler))

    def lookup(self, exception):
        """
        Lookup the existing instance of :class:`ErrorHandler` and fetch the
        registered handler for a specific type of exception.

        This method leverages a dict lookup to speedup the retrieval process.

        :param exception: Type of exception

        :type exception: :class:`sanic.exceptions.SanicException` or
            :class:`Exception`

        :return: Registered function if found ``None`` otherwise
        """
        # 从缓存中获得已注册错误处理器
        exception_type = type(exception)
        handler = self.cached_handlers.get(exception_type, self._missing)
        # 如果缓存中没有找到对应的处理器，则加入缓存
        if handler is self._missing:
            for exception_class, handler in self.handlers:
                if isinstance(exception, exception_class):
                    self.cached_handlers[exception_type] = handler
                    return handler
            self.cached_handlers[exception_type] = None
            handler = None
        return handler

    def response(self, request, exception):
        """Fetches and executes an exception handler and returns a response
        object

        :param request: Instance of :class:`sanic.request.Request`
        :param exception: Exception to handle

        :type request: :class:`sanic.request.Request`
        :type exception: :class:`sanic.exceptions.SanicException` or
            :class:`Exception`

        :return: Wrap the return value obtained from :func:`default`
            or registered handler for that type of exception.
        """
        # 查找已注册的处理器
        handler = self.lookup(exception)
        response = None
        try:
            # 执行错误处理器
            if handler:
                response = handler(request, exception)
            # 如果错误处理器不返回内容，则继续执行默认错误处理器
            if response is None:
                response = self.default(request, exception)
        except Exception:
            # 错误处理器执行异常返回500响应
            self.log(format_exc())
            # 获得请求地址
            try:
                url = repr(request.url)
            except AttributeError:
                url = "unknown"
            response_message = (
                "Exception raised in exception handler " '"%s" for uri: %s'
            )
            logger.exception(response_message, handler.__name__, url)

            if self.debug:
                return text(response_message % (handler.__name__, url), 500)
            else:
                return text("An error occurred while handling an error", 500)
        return response

    def log(self, message, level="error"):
        """
        Deprecated, do not use.
        """

    def default(self, request, exception):
        """默认错误处理
        Provide a default behavior for the objects of :class:`ErrorHandler`.
        If a developer chooses to extent the :class:`ErrorHandler` they can
        provide a custom implementation for this method to behave in a way
        they see fit.

        :param request: Incoming request
        :param exception: Exception object

        :type request: :class:`sanic.request.Request`
        :type exception: :class:`sanic.exceptions.SanicException` or
            :class:`Exception`
        :return:
        """
        quiet = getattr(exception, "quiet", False)
        if quiet is False:
            try:
                url = repr(request.url)
            except AttributeError:
                url = "unknown"

            self.log(format_exc())
            logger.exception("Exception occurred while handling uri: %s", url)

        # 返回默认错误响应
        return exception_response(request, exception, self.debug)


class ContentRangeHandler:
    """
    A mechanism to parse and process the incoming request headers to
    extract the content range information.

    :param request: Incoming api request
    :param stats: Stats related to the content

    :type request: :class:`sanic.request.Request`
    :type stats: :class:`posix.stat_result`

    :ivar start: Content Range start
    :ivar end: Content Range end
    :ivar size: Length of the content
    :ivar total: Total size identified by the :class:`posix.stat_result`
        instance
    :ivar ContentRangeHandler.headers: Content range header ``dict``
    """

    __slots__ = ("start", "end", "size", "total", "headers")

    def __init__(self, request, stats):
        self.total = stats.st_size
        _range = request.headers.get("Range")
        if _range is None:
            raise HeaderNotFound("Range Header Not Found")
        unit, _, value = tuple(map(str.strip, _range.partition("=")))
        if unit != "bytes":
            raise InvalidRangeType(
                "%s is not a valid Range Type" % (unit,), self
            )
        start_b, _, end_b = tuple(map(str.strip, value.partition("-")))
        try:
            self.start = int(start_b) if start_b else None
        except ValueError:
            raise ContentRangeError(
                "'%s' is invalid for Content Range" % (start_b,), self
            )
        try:
            self.end = int(end_b) if end_b else None
        except ValueError:
            raise ContentRangeError(
                "'%s' is invalid for Content Range" % (end_b,), self
            )
        if self.end is None:
            if self.start is None:
                raise ContentRangeError(
                    "Invalid for Content Range parameters", self
                )
            else:
                # this case represents `Content-Range: bytes 5-`
                self.end = self.total - 1
        else:
            if self.start is None:
                # this case represents `Content-Range: bytes -5`
                self.start = self.total - self.end
                self.end = self.total - 1
        if self.start >= self.end:
            raise ContentRangeError(
                "Invalid for Content Range parameters", self
            )
        self.size = self.end - self.start + 1
        self.headers = {
            "Content-Range": "bytes %s-%s/%s"
            % (self.start, self.end, self.total)
        }

    def __bool__(self):
        return self.size > 0
