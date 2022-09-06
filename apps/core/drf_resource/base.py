# -*- coding: utf-8 -*-

import logging
from abc import abstractmethod, ABCMeta
from typing import Dict, List, Union, Optional

from django.db import models
from django.utils.translation import gettext as _
from opentelemetry import trace

from rest_framework.exceptions import APIException
from xTool.plugin import (
    register_plugin)

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


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
        plugin_type = getattr(new_class, "plugin_type")
        if not plugin_type:
            raise Exception("plugin_type not set in class %s" % class_name)
        register_plugin(plugin_type, class_name)(new_class)
        return new_class


class Resource(metaclass=ResourceMeta):
    RequestSerializer = None
    ResponseSerializer = None

    many_request_data = False
    many_response_data = False

    def __init__(self) -> None:
        self._request_serializer_obj = None
        self._response_serializer_obj = None

    @classmethod
    def get_resource_name(cls):
        return cls.__name__

    def __call__(self, request_data: Optional[Dict] = None):
        # thread safe
        tmp_resource = self.__class__()
        return tmp_resource.request(request_data)

    def request(self,
                request_data: Optional[Dict] = None) -> Union[List, Dict]:
        """执行完整的请求 ."""
        span_name = f"drf_resource/{self.get_resource_name()}"
        with tracer.start_as_current_span(span_name):
            # 验证请求参数
            validated_request_data = self.validate_request_data(request_data)
            # 执行请求操作
            response_data = self.perform_request(validated_request_data)
            # 验证响应结果
            validated_response_data = self.validate_response_data(
                response_data)
            return validated_response_data

    def validate_request_data(self,
                              request_data: Optional[Dict]) -> Optional[Dict]:
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
        if isinstance(request_data, (models.Model, models.QuerySet)):
            request_serializer_obj = self.RequestSerializer(
                request_data, many=self.many_request_data)
            # 返回传出的原始数据
            result = request_serializer_obj.data
        else:
            request_serializer_obj = self.RequestSerializer(
                data=request_data, many=self.many_request_data)
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
    def perform_request(
        self, validated_request_data: Optional[Dict]) -> Union[List, Dict]:
        """执行请求操作 ."""
        ...

    def validate_response_data(
        self, response_data: Union[List, Dict]) -> Union[List, Dict]:
        """验证请求返回的数据 ."""
        if not self.ResponseSerializer:
            return response_data

        # model类型的数据需要特殊处理
        if isinstance(response_data, (models.Model, models.QuerySet)):
            response_serializer_obj = self.ResponseSerializer(
                response_data, many=self.many_response_data)
            result = response_serializer_obj.data
        else:
            response_serializer_obj = self.ResponseSerializer(
                data=response_data, many=self.many_response_data)
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
