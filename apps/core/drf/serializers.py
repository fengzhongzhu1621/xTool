from datetime import datetime

from django.utils.translation import gettext as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class DateTimeField(serializers.CharField):
    def run_validators(self, value):
        super().run_validators(value)
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValidationError(detail=_("当前输入非日期时间格式，请按格式[年-月-日 时:分:秒]填写"))
