from abc import ABCMeta, abstractmethod
from typing import Dict, List, Optional, Union

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException

from core.drf_resource.logger import logger, tracer
from xTool.plugin import register_plugin


class ResourceMeta(ABCMeta):
    """自动注册资源类 ."""

    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, ResourceMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        new_class = super_new(cls, name, bases, attrs)
        class_name = new_class.__name__
        # 自动注册资源类
        plugin_type = getattr(new_class, "plugin_type", None)
        if not plugin_type:
            return new_class
        # 注册为一个插件
        register_plugin(plugin_type, class_name)(new_class)
        return new_class


class Resource(metaclass=ResourceMeta):
    """资源基类 ."""

    RequestSerializer = None  # 请求序列化器
    ResponseSerializer = None  # 响应序列化器

    many_request_data = None
    many_response_data = None

    def __init__(self) -> None:
        self._request_serializer_obj = None
        self._response_serializer_obj = None

    @classmethod
    def get_resource_name(cls):
        """获得资源名称 ."""
        return cls.__name__

    @property
    def request_serializer(self):
        return self._request_serializer_obj

    @property
    def response_serializer(self):
        return self._response_serializer_obj

    def __call__(self, *args, **kwargs):
        start_time = timezone.now()
        request_data = {"args": args, "kwargs": kwargs}
        tmp_resource = self.__class__()
        try:
            response_data = tmp_resource.request(*args, **kwargs)
        except Exception as exc_info:
            logger.exception(exc_info)
            response_data = str(exc_info)
            raise exc_info
        finally:
            end_time = timezone.now()
            name = f"{tmp_resource.__class__.__module__}.{tmp_resource.__class__.__name__}"
            logger.info(
                "Resource => %s, StartTime => %s, EndTime => %s, RequestData => %s, ResponseData = %s",
                name,
                start_time,
                end_time,
                request_data,
                response_data,
            )

            return response_data

    def request(self, request_data: Optional[Dict] = None, *args, **kwargs) -> Union[List, Dict]:
        """执行入口 ."""
        request_data = request_data or kwargs
        span_name = f"drf_resource/{self.get_resource_name()}"
        with tracer.start_as_current_span(span_name):
            # 验证请求参数
            validated_request_data = self.validate_request_data(request_data)
            # 执行请求操作
            response_data = self.perform_request(validated_request_data, *args, **kwargs)
            # 验证响应结果
            validated_response_data = self.validate_response_data(response_data)
            return validated_response_data

    def validate_request_data(self, request_data: Optional[Dict]) -> Optional[Dict]:
        """验证请求参数 ."""
        if not self.RequestSerializer:
            # 不进行参数验证
            return request_data
        # In particular, if a `data=` argument is passed then:
        # .is_valid() - Available.
        # .initial_data - Available.
        # .validated_data - Only available after calling `is_valid()`
        # .errors - Only available after calling `is_valid()`
        # .data - Only available after calling `is_valid()`
        many_request_data = bool(self.many_request_data)
        if isinstance(request_data, (models.Model, models.QuerySet)):
            request_serializer_obj = self.RequestSerializer(request_data, many=many_request_data)
            # 返回传出的原始数据
            result = request_serializer_obj.data
        else:
            many_request_data = isinstance(request_data, List)
            request_serializer_obj = self.RequestSerializer(data=request_data, many=many_request_data)
            # 验证输入参数
            if not request_serializer_obj.is_valid():
                errors = request_serializer_obj.errors
                resource_name = self.get_resource_name()
                err_message = _(f"Resource[{resource_name}] 请求参数格式错误：{errors}")
                logger.error(err_message)
                raise APIException(err_message)
            # 返回经过验证后的传入数据
            result = request_serializer_obj.validated_data

        self._request_serializer_obj = request_serializer_obj
        return result

    @abstractmethod
    def perform_request(self, validated_request_data: Optional[Dict], *args, **kwargs) -> Union[List, Dict, None]:
        """执行请求操作 ."""
        ...

    def validate_response_data(self, response_data: Union[List, Dict]) -> Union[List, Dict, None]:
        """验证请求返回的数据 ."""
        if not self.ResponseSerializer:
            # 没有响应序列化器则直接返回结果
            return response_data

        # model类型的数据需要特殊处理
        many_response_data = bool(self.many_response_data)
        if isinstance(response_data, (models.Model, models.QuerySet)):
            response_serializer_obj = self.ResponseSerializer(response_data, many=many_response_data)
            result = response_serializer_obj.data
        else:
            many_response_data = isinstance(many_response_data, List)
            response_serializer_obj = self.ResponseSerializer(data=response_data, many=many_response_data)
            self._response_serializer_obj = response_serializer_obj
            if not response_serializer_obj.is_valid():
                errors = response_serializer_obj.errors
                resource_name = self.get_resource_name()
                err_message = _(f"Resource[{resource_name}] 返回参数格式错误：{errors}")
                logger.error(err_message)
                raise APIException(err_message)
            result = response_serializer_obj.validated_data
        self._response_serializer_obj = response_serializer_obj
        return result
