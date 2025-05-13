import json
from contextlib import contextmanager

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from opentelemetry import trace
from opentelemetry.instrumentation.django import _DjangoMiddleware
from opentelemetry.trace import Status, StatusCode, get_current_span
from opentelemetry.trace.span import Span
from rest_framework.response import Response

from apps.logger import logger
from bk_resource import BkApiResource as BkApiResourceBase
from bk_resource.exceptions import APIRequestError
from bk_resource.settings import bk_resource_settings
from bk_resource.utils.request import get_resource_by_request
from core.drf.exception import custom_exception_handler


def instrument_hook():
    """自定义 span name ."""
    origin_func = _DjangoMiddleware._get_span_name
    _DjangoMiddleware._get_span_name = get_span_name
    setattr(_DjangoMiddleware, "_origin_get_span_name", origin_func)


def get_span_name(_, request):
    """获取 django instrument 生成的 span 的 span_name 返回 Resource的路径"""
    # 根据 request 对象获取具体的 Resource 类
    resource_clz = get_resource_by_request(request)
    if resource_clz:
        return f"{resource_clz.__module__}.{resource_clz.__qualname__}"
    # 使用默认实现获取
    return _DjangoMiddleware._origin_get_span_name(_, request)  # pylint: disable=protected-access # noqa


class Tracer:
    """trace 工具类，解决国际化字符串问题 ."""

    @classmethod
    def _to_raw(cls, attributes, span_name):
        attrs = {}
        for k, v in attributes.items():
            t_v = v
            if isinstance(v, (list, dict)):
                t_v = json.dumps(v, cls=DjangoJSONEncoder)
            else:
                t_v = str(t_v)
            attrs[k] = t_v

        return attrs, str(span_name)

    @classmethod
    def create_span(cls, span_name, attributes=None, kind=None, status=None, context=None, **kwargs):
        tracer = trace.get_tracer(__name__)

        attributes = attributes or {}
        attrs, span_name = cls._to_raw(attributes, span_name)

        params = {}
        if kind:
            params["kind"] = kind

        span = tracer.start_span(str(span_name), attributes=attrs, context=context, **params, **kwargs)
        if status:
            span.set_status(Status(status))

        return span

    @classmethod
    @contextmanager
    def as_current_span(cls, span_name, kind=None, attributes=None, status=None, context=None, **kwargs) -> Span:

        tracer = trace.get_tracer(__name__)

        params = {}
        if kind:
            params["kind"] = kind

        with tracer.start_as_current_span(
            span_name, attributes=attributes, context=context, **params, **kwargs
        ) as span:

            if status:
                span.set_status(Status(status))

            yield span

            span.set_status(Status(StatusCode.OK))


def trace_exception_handler(exc, context) -> Response:
    response = custom_exception_handler(exc, context)
    span = get_current_span()
    trace_info = (
        f" [请求信息] TraceId : {format(span.get_span_context().trace_id, '032x')} "
        f"SpanId : {format(span.get_span_context().span_id, '016x')}"
    )

    if isinstance(response.data, dict):
        response.data["trace"] = trace_info
    else:
        response.data = str(response.data) + trace_info

    span.record_exception(exc)

    return response


class BkApiResource(BkApiResourceBase):
    """增加了 Trace 功能的 BkApiResource"""

    def perform_request(self, validated_request_data):
        span_name = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        tags = [str(tag) for tag in self.tags]
        with Tracer.as_current_span(
            span_name,
            attributes={
                "request.apigw.api.name": str(self.name),
                "request.apigw.api.tags": str(",".join(tags) if tags else ""),
                "request.apigw.api.platform_auth": self.platform_authorization,
                "request.apigw.api.method": self.method,
                "request.apigw.api.module_name": self.module_name,
            },
        ) as span:
            res = self._perform_request(validated_request_data)
            span.set_status(Status(StatusCode.OK))
            return res

    def _perform_request(self, validated_request_data):
        """
        发起http请求
        """
        span_name = f"{self.__class__.__module__}.{self.__class__.__qualname__}"

        validated_request_data = dict(validated_request_data)
        validated_request_data = self.build_request_data(validated_request_data)

        # 拼接最终请求的url
        request_url = self.build_url(validated_request_data)
        logger.debug("request: {}".format(request_url))

        # 构造请求头
        headers = self.build_header(validated_request_data)
        kwargs = {
            "method": self.method,
            "url": request_url,
            "timeout": self.TIMEOUT,
            "headers": headers,
            "verify": bk_resource_settings.REQUEST_VERIFY,
        }

        try:
            if self.method == "GET":
                kwargs["params"] = validated_request_data
                kwargs = self.before_request(kwargs)
                if settings.BKAPP_RESOURCE_DEBUG:
                    logger.info("BKAPP_RESOURCE_DEBUG %s %s", span_name, json.dumps(kwargs))
                request_url = kwargs.pop("url")
                if "method" in kwargs:
                    del kwargs["method"]
                response = self.session.get(request_url, **kwargs)
            else:
                non_file_data, file_data = self.split_request_data(validated_request_data)
                if not file_data:
                    # 不存在文件数据，则按照json方式去请求
                    kwargs["json"] = non_file_data
                else:
                    # 若存在文件数据，则将非文件数据和文件数据分开传参
                    kwargs["files"] = file_data
                    kwargs["data"] = non_file_data

                kwargs = self.before_request(kwargs)
                if settings.BKAPP_RESOURCE_DEBUG:
                    logger.info("BKAPP_RESOURCE_DEBUG %s %s", span_name, json.dumps(kwargs))
                response = self.session.request(**kwargs)
        except Exception as err:
            logger.exception(f"APIRequestFailed => {err}")
            err_message = err.__doc__ or err.__class__.__name__
            raise APIRequestError(
                module_name=self.module_name,
                url=self.action,
                result=err_message,
            ) from err
        return self.parse_response(response)
