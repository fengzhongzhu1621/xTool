from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy
from rest_framework import serializers


class ModifyPasswordRandomCycleSerializer(serializers.Serializer):
    class CrontabSerializer(serializers.Serializer):
        minute = serializers.CharField(help_text=_lazy("分钟"))
        hour = serializers.CharField(help_text=_lazy("小时"))
        day_of_week = serializers.CharField(
            help_text=_lazy("每周几天(eg: 1,4,5 表示一周的周一，周四，周五)"), required=False
        )
        day_of_month = serializers.CharField(
            help_text=_lazy("每月几天(eg: 1, 11, 13 表示每月的1号，11号，13号)"), required=False
        )

    crontab = CrontabSerializer(help_text=_lazy("crontab表达式"))


class PasswordPolicySerializer(serializers.Serializer):
    class PolicySerializer(serializers.Serializer):
        class IncludeRuleSerializer(serializers.Serializer):
            numbers = serializers.BooleanField(help_text=_lazy("是否包含数字"))
            symbols = serializers.BooleanField(help_text=_lazy("是否包含特殊符号"))
            lowercase = serializers.BooleanField(help_text=_lazy("是否包含小写字符"))
            uppercase = serializers.BooleanField(help_text=_lazy("是否包含大写字符"))

        class ExcludeContinuousRuleSerializer(serializers.Serializer):
            limit = serializers.IntegerField(help_text=_lazy("最大连续长度"))
            letters = serializers.BooleanField(help_text=_lazy("是否限制连续字母"))
            numbers = serializers.BooleanField(help_text=_lazy("是否限制连续数字"))
            repeats = serializers.BooleanField(help_text=_lazy("是否限制连续重复字符"))
            symbols = serializers.BooleanField(help_text=_lazy("是否限制连续特殊字符"))
            keyboards = serializers.BooleanField(help_text=_lazy("是否限制连续键盘序"))

        max_length = serializers.IntegerField(help_text=_lazy("最大长度"))
        min_length = serializers.IntegerField(help_text=_lazy("最小长度"))
        include_rule = IncludeRuleSerializer(help_text=_lazy("包含规则"))
        exclude_continuous_rule = ExcludeContinuousRuleSerializer(help_text=_lazy("排除连续性规则"))

    rule = serializers.PolicySerializer(help_text=_lazy("密码安全策略"), required=False)
    name = serializers.CharField(help_text=_lazy("密码安全规则策略名称"))
    id = serializers.IntegerField(help_text=_lazy("密码安全规则策略id"))
    reset = serializers.BooleanField(help_text=_lazy("是否重置"), required=False, default=False)

    def validate(self, attrs):
        if not attrs.get("reset"):
            if not attrs.get("rule"):
                raise serializers.ValidationError(_("缺少参数: rule!"))
            try:
                if int(attrs["rule"]["max_length"]) < int(attrs["rule"]["min_length"]):
                    raise serializers.ValidationError(_("密码最小长度不能大于最大长度"))
            except ValueError:
                raise serializers.ValidationError(_("请确保密码长度范围为整型"))

        return attrs
