from django.utils.translation import gettext_lazy as _lazy

from apps.global_conf.serializers import GenerateQueryTokenSerializer, GetQueryDataSerializer
from core.cache import CacheKey
from core.constants import TimeEnum
from xTool.codec import count_md5

from .base import GlobalConfBaseResource


class CacheGenerateToken(CacheKey):
    key_template = "generate_request_token:{token}"


class GenerateQueryTokenResource(GlobalConfBaseResource):
    name = _lazy("创建请求参数的 token")
    RequestSerializer = GenerateQueryTokenSerializer

    def perform_request(self, validated_request_data):
        """计算并返回query_token值"""
        # 生成请求参数的 md5
        token = count_md5(validated_request_data)
        cache = CacheGenerateToken(token=token)
        # 缓存请求参数
        query_data = validated_request_data["query_data"]
        cache.set(query_data, TimeEnum.ONE_DAY_SECOND.value)

        return {"query_token": token}


class GetQueryDataResource(GlobalConfBaseResource):
    name = _lazy("通过query_token获取请求数据")
    RequestSerializer = GetQueryDataSerializer

    def perform_request(self, validated_request_data):
        """获取所有工单列表请求query_data"""
        token = validated_request_data.get("query_token")
        cache = CacheGenerateToken(token=token)
        value = cache.get()
        return {"query_data": value}
