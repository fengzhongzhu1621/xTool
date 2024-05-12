from django.utils.translation import gettext_lazy as _lazy
from rest_framework import serializers


class GenerateQueryTokenSerializer(serializers.Serializer):
    key = serializers.CharField(required=True, label=_lazy("标识"))
    query_data = serializers.JSONField(required=True, label=_lazy("查询条件"))


class GetQueryDataSerializer(serializers.Serializer):
    query_token = serializers.CharField(label=_lazy("token 值"))
