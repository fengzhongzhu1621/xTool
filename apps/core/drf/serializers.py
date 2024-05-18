from typing import Dict

import orjson as json
from bk_resource.exceptions import ValidateException
from django.db import models
from django.utils.translation import gettext_lazy as _lazy
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DrfValidationError
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer as DrfModelSerializer
from rest_framework.settings import api_settings
from rest_framework.utils import model_meta

from apps.core.drf.serializer_fields import CustomDateTimeField
from apps.core.exceptions import ParamValidationError
from apps.core.models import MultiStrSplitCharField, MultiStrSplitTextField


class FilterConditionSerializer(serializers.Serializer):
    class ContentSerializer(serializers.Serializer):
        field = serializers.CharField(label=_lazy("查询字段"), required=True)
        operator = serializers.CharField(label=_lazy("操作符"), required=True)
        value = serializers.CharField(label=_lazy("操作值"), required=True)

    condition = serializers.CharField(label=_lazy("操作符"), required=True)
    rules = ContentSerializer(label=_lazy("规则"), required=True, many=True)


class GeneralSerializer(DrfModelSerializer):
    """
    自定义ModelSerializer序列化器
    """

    def __init__(self, instance=None, data=empty, **kwargs):
        self.serializer_field_mapping[models.DateTimeField] = CustomDateTimeField
        self.serializer_field_mapping[MultiStrSplitCharField] = serializers.ListField
        self.serializer_field_mapping[MultiStrSplitTextField] = serializers.ListField
        super(GeneralSerializer, self).__init__(instance=instance, data=data, **kwargs)

    def is_valid(self, raise_exception=False):
        """
        参数校验 返回为处理后的异常信息
        """
        try:
            super().is_valid(raise_exception)
        # 捕获原生的参数校验异常，抛出SaaS封装的参数校验异常
        except DrfValidationError:
            if self._errors and raise_exception:
                errors = format_serializer_errors(self.errors, self.fields, self.initial_data)
                raise ParamValidationError(
                    errors,
                )

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


class ModelSerializer(GeneralSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        self.serializer_field_mapping[models.DateTimeField] = CustomDateTimeField
        self.serializer_field_mapping[MultiStrSplitCharField] = serializers.ListField
        self.serializer_field_mapping[MultiStrSplitTextField] = serializers.ListField
        super().__init__(instance=instance, data=data, **kwargs)

    def is_valid(self, raise_exception=False):
        try:
            super().is_valid(raise_exception)
        # 捕获原生的参数校验异常，抛出SaaS封装的参数校验异常
        except DrfValidationError:
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


def format_serializer_errors(  # pylint: disable=too-many-locals,too-many-branches
    errors, fields, params, prefix="", return_all_errors=True
):
    """
    格式化序列化器的错误，对前端显示更为友好
    :param errors: serializer_errors
    :param fields: 校验的字段
    :param params: 参数
    :param prefix: 错误消息前缀
    :param return_all_errors: 是否返回所有错误消息
    :return:
    """
    message = {}
    cn_message = {}
    for key, field_errors in list(errors.items()):  # pylint: disable=too-many-nested-blocks
        sub_message = []
        try:
            label = fields[key].label
        except (KeyError, AttributeError):
            label = key

        if key == api_settings.NON_FIELD_ERRORS_KEY:
            sub_message.append(";".join(field_errors))
        elif key not in fields:
            sub_message.append(json.dumps(field_errors, ensure_ascii=False))
        else:
            field = fields[key]
            if (
                hasattr(field, "child")
                and isinstance(field_errors, list)
                and len(field_errors) > 0
                and not isinstance(field_errors[0], str)
            ):
                for index, sub_errors in enumerate(field_errors):
                    if sub_errors:
                        sub_format = format_serializer_errors(sub_errors, field.child.fields, params, prefix=prefix)
                        if not return_all_errors:
                            return f"{label}: {sub_format}"
                        temp_message = f"{prefix}第{index + 1}项:"
                        sub_message.append(
                            temp_message + sub_format[0] if isinstance(sub_format, tuple) else sub_format
                        )
            else:
                if isinstance(field_errors, dict):
                    if hasattr(field, "child"):
                        sub_format = format_serializer_errors(field_errors, field.child.fields, params, prefix=prefix)
                    else:
                        sub_format = format_serializer_errors(field_errors, field.fields, params, prefix=prefix)
                    if not return_all_errors:
                        return f"{label}: {sub_format}"
                    sub_message.append(sub_format)
                elif isinstance(field_errors, list):
                    for index, error in enumerate(field_errors):
                        error = error.format(**{key: params.get(key, "")})
                        if len(field_errors) > 1:
                            sub_message.append("{index}.{error}".format(index=index + 1, error=error))
                        else:
                            sub_message.append("{error}".format(error=error))
                        if not return_all_errors:
                            sub_message = ",".join(sub_message)
                            return f"{label}: {sub_message}"
        cn_message[str(label)] = ",".join(
            [str(message[1]) if isinstance(message, tuple) else str(message) for message in sub_message]
        )
        message[key] = sub_message

    message = json.dumps(message, ensure_ascii=False)
    cn_message = json.dumps(cn_message, ensure_ascii=False)
    return message, cn_message


def custom_params_valid(serializer, params, instance=None, many=False, partial=False):
    """序列化器自定义数据校验"""
    _serializer = serializer(data=params, many=many, instance=instance, partial=partial)
    try:
        _serializer.is_valid(raise_exception=True)
    except serializers.ValidationError:
        msg_tuple = format_serializer_errors(_serializer.errors, _serializer.fields, params)
        raise ParamValidationError(msg_tuple)
    if many:
        return list(_serializer.validated_data)

    return dict(_serializer.validated_data)
