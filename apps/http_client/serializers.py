from django.utils.translation import gettext_lazy as _lazy
from rest_framework import serializers


class RequestApiConfigSerializer(serializers.Serializer):
    platform_authorization = serializers.BooleanField(label=_lazy("是否使用平台账号"), default=False)
    action = serializers.CharField(label=_lazy("资源名称"), required=True, allow_blank=True)
    base_url = serializers.CharField(label=_lazy("请求地址"), required=True)
    method = serializers.CharField(label=_lazy("请求方法"), required=True)
    module_name = serializers.CharField(label=_lazy("所属模块"), required=True)
    request_param_template = serializers.JSONField(label=_lazy("请求参数模板"), required=True)
    request_context = serializers.JSONField(label=_lazy("请求参数上下文"), required=True)


class SendRequestSerializer(serializers.Serializer):
    platform_authorization = serializers.BooleanField(label=_lazy("是否使用平台账号"), default=False)
    system_code = serializers.CharField(label=_lazy("系统编码"), required=True)
    api_code = serializers.CharField(label=_lazy("API编码"), required=True)
    request_context = serializers.JSONField(label=_lazy("请求参数上下文"), required=True)
