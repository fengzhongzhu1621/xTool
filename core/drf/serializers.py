from typing import Dict

import orjson as json
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer as DrfModelSerializer
from rest_framework.utils import model_meta

from bk_resource.exceptions import ValidateException
from bk_resource.tools import format_serializer_errors as bk_resource_format_serializer_errors
from bk_resource.utils.logger import logger
from core.constants import LEN_SHORT
from core.drf.format import format_serializer_errors
from core.drf.serializer_fields import CustomDateTimeField
from core.exceptions import ParamValidationError
from core.models import MultiStrSplitCharField, MultiStrSplitTextField


class FilterConditionSerializer(serializers.Serializer):
    class ContentSerializer(serializers.Serializer):
        field = serializers.CharField(label=_lazy("查询字段"), required=True)
        operator = serializers.CharField(label=_lazy("操作符"), required=True)
        value = serializers.CharField(label=_lazy("操作值"), required=True)

    condition = serializers.CharField(label=_lazy("操作符"), required=True)
    rules = ContentSerializer(label=_lazy("规则"), required=True, many=True)


class GeneralSerializer(serializers.Serializer):
    """
    自定义ModelSerializer序列化器
    """

    def is_valid(self, raise_exception=True):
        try:
            super().is_valid(raise_exception)
        # 捕获原生的参数校验异常，抛出SaaS封装的参数校验异常
        except ValidationError:
            if self._errors and raise_exception:
                err_message = ""
                error = format_serializer_errors(self)
                if isinstance(error, dict):
                    for key, value in error.items():
                        # 只显示一种错误信息
                        err_message = f"{key}: {value}"
                        break
                else:
                    err_message = str(error)
                msg = _("request_data=%s, 请求参数格式错误：%s") % (
                    self.initial_data,
                    bk_resource_format_serializer_errors(self),
                )
                logger.error(msg)
                raise ValidateException(err_message)
        except ParamValidationError as exc_info:
            args = exc_info.args[0]
            if isinstance(args, tuple) and len(args) == 2:
                err = json.loads(args[1])
                if err and isinstance(err, dict):
                    raise ValidateException(list(err.values())[0])
            raise

        return not bool(self._errors)


class ModelSerializer(DrfModelSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        self.serializer_field_mapping[models.DateTimeField] = CustomDateTimeField
        self.serializer_field_mapping[MultiStrSplitCharField] = serializers.ListField
        self.serializer_field_mapping[MultiStrSplitTextField] = serializers.ListField
        super().__init__(instance=instance, data=data, **kwargs)

    def is_valid(self, raise_exception=False):
        try:
            super().is_valid(raise_exception)
        # 捕获原生的参数校验异常，抛出SaaS封装的参数校验异常
        except ValidationError:
            if self._errors and raise_exception:
                raise ValidateException(
                    format_serializer_errors(self),
                )
        except ParamValidationError as exc_info:
            args = exc_info.args[0]
            if isinstance(args, tuple) and len(args) == 2:
                err = json.loads(args[1])
                if err and isinstance(err, dict):
                    raise ValidateException(list(err.values())[0])
            raise

        return not bool(self._errors)

    def create(self, validated_data: Dict) -> object:
        """
        序列化器创建数据
        """
        model_class = self.Meta.model

        info = model_meta.get_field_info(model_class)
        many_to_many = {}
        for field_name, relation_info in list(info.relations.items()):
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = model_class.objects.create(**validated_data)
        except TypeError as exc:
            msg = (
                "Got a `TypeError` when calling `%s.objects.create()`. "
                "This may be because you have a writable field on the "
                "serializer class that is not a valid argument to "
                "`%s.objects.create()`. You may need to make the field "
                "read-only, or override the %s.create() method to handle "
                "this correctly.\nOriginal exception text was: %s."
                % (
                    model_class.__name__,
                    model_class.__name__,
                    self.__class__.__name__,
                    exc,
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in list(many_to_many.items()):
                setattr(instance, field_name, value)

        return instance

    class Meta:
        """
        元数据定义
        """

        model = None


class PageSerializer(serializers.Serializer):
    """
    分页序列化器
    """

    page = serializers.IntegerField(help_text=_lazy("页数"))
    page_size = serializers.IntegerField(help_text=_lazy("每页数量"))
    ordering = serializers.CharField(label=_lazy("排序字段"), max_length=LEN_SHORT, allow_null=True, default=None)


class PageConditionSerializer(serializers.Serializer):
    start = serializers.IntegerField(label=_lazy("记录开始位置"), required=True, min_value=0)
    limit = serializers.IntegerField(label=_lazy("每页限制条数，最大500"), required=True, min_value=1, max_value=500)


class SearchSerializer(serializers.Serializer):
    """
    关键字序列化器
    """

    search = serializers.CharField(help_text=_lazy("模糊查找，多个查找关键字以`,`分隔"), required=False)


class PostFilterSerializer(serializers.Serializer):
    """
    ORM condition查询序列化器
    example:
    {
        "conditions": [
            {
                "fields": ["name"],
                "operator": "in",
                "values": ["user1", "user2"]
            }
        ]
    }
    """

    class ConditionSerializer(serializers.Serializer):
        """
        单个查询条件序列化器
        """

        fields = serializers.ListField(help_text=_lazy("查询目标字段列表"), child=serializers.CharField(), min_length=1)
        operator = serializers.CharField(
            help_text=_lazy("查询类型，可选：`in` `contains` `range` `gt(lt)` `gte(lte)...")
        )
        values = serializers.ListField(help_text=_lazy("查询目标值列表"), min_length=1)

    conditions = serializers.ListField(
        help_text=_lazy("查询条件"), child=ConditionSerializer(), required=False, default=[]
    )
