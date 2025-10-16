from datetime import datetime

from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.exceptions import ParamValidationError
from core.utils import strftime_local


class MultipleIntField(serializers.Field):
    """
    用于整数多选查询的字段
    """

    def to_internal_value(self, data):  # pylint: disable=no-self-use
        """
        Transform the *incoming* primitive data into a native value.
        """
        ret = []
        for value in data.split(","):
            try:
                ret.append(int(value))
            except ValueError:
                raise ParamValidationError(_("请求参数必须全部为整数"))
        return ret

    def to_representation(self, value):  # pylint: disable=no-self-use
        """
        Transform the *outgoing* native value into primitive data.
        """
        return value


class MultipleStrField(serializers.Field):
    """
    用于字符串多选查询的字段
    """

    def to_internal_value(self, data):  # pylint: disable=no-self-use
        """
        Transform the *incoming* primitive data into a native value.
        """
        data = [str(value) for value in data.split(",")]
        return data

    def to_representation(self, value):  # pylint: disable=no-self-use
        """
        Transform the *outgoing* native value into primitive data.
        """
        return value


class CustomDateTimeField(serializers.DateTimeField):
    """
    自定义数据库时间字段
    """

    def to_representation(self, value):  # pylint: disable=no-self-use
        """
        Transform the *outgoing* native value into primitive data.
        """
        if not value:
            return None

        return strftime_local(
            value,
            fmt=settings.REST_FRAMEWORK.get("DATETIME_FORMAT", "%Y-%m-%d %H:%M:%S%z"),
        )


class DateTimeField(serializers.CharField):
    def run_validators(self, value):
        super().run_validators(value)
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValidationError(detail=_("当前输入非日期时间格式，请按格式[年-月-日 时:分:秒]填写"))


class ListMultipleChoiceField(serializers.MultipleChoiceField):
    """
    类型为List的MultipleChoiceField
    """

    def to_internal_value(self, data) -> list:
        data = list(super().to_internal_value(data))
        data.sort()
        return data

    def to_representation(self, value):
        value = list(super().to_representation(value))
        value.sort()
        return value
