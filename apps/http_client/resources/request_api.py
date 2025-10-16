from typing import Dict

from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from apps.http_client.serializers import (
    RequestApiConfigSerializer,
    SendRequestSerializer,
)
from apps.http_client.utils import fetch_request_api_config
from bk_resource import APIResource
from bk_resource.exceptions import ValidateException
from core.templates.render import jinja_render

from .base import HttpClientBaseResource


class RequestApiConfigResource(APIResource):
    action = None
    method = "POST"
    base_url = None
    module_name = None
    platform_authorization = False
    RequestSerializer = RequestApiConfigSerializer

    @staticmethod
    def render_request_template(validated_request_data: Dict) -> Dict:
        """使用上下文渲染请求参数模板."""
        request_param_template = validated_request_data["request_param_template"]
        context = validated_request_data["request_context"]
        request_data = jinja_render(request_param_template, context)

        return request_data

    def build_request_data(self, validated_request_data: Dict) -> Dict:
        """构造API请求参数 ."""
        self.platform_authorization = validated_request_data["platform_authorization"]
        self.action = validated_request_data["action"]
        self.method = validated_request_data["method"].upper()
        self.base_url = validated_request_data["base_url"]
        self.module_name = validated_request_data["module_name"]
        # 使用上下文渲染请求参数模板
        request_data = self.render_request_template(validated_request_data)
        request_data = super().build_request_data(request_data)

        return request_data

    def build_url(self, validated_request_data: Dict) -> Dict:
        url = super().build_url(validated_request_data)
        url = url.format(**validated_request_data)

        return url


class SendRequestResource(HttpClientBaseResource):
    """
    通过API名称调用系统API
    """

    name = _lazy("通过API名称调用系统API")
    RequestSerializer = SendRequestSerializer

    @staticmethod
    def validate_method(method: str) -> None:
        """验证请求方 ."""
        if method.upper() not in ["GET", "POST"]:
            raise ValidateException(_("仅支持GET或POST请求，当前为 请求" % method.upper()))

    def validate_request_data(self, request_data: Dict) -> Dict:
        """验证参数并获取api配置 ."""
        request_data = super().validate_request_data(request_data)

        # 获取最新的 API 配置信息
        system_code = request_data["system_code"]
        api_code = request_data["api_code"]
        api_config = fetch_request_api_config(system_code, api_code)
        if not api_config:
            raise ValidateException(_("API配置不存在"))
        request_data["api_config"] = api_config

        return request_data

    def perform_request(self, validated_request_data: Dict) -> Dict:
        api_config = validated_request_data["api_config"]

        platform_authorization = validated_request_data["platform_authorization"]
        request_context = validated_request_data["request_context"]
        system_code = validated_request_data["system_code"]

        action = api_config["path"]
        base_url = api_config["system"]["domain"]
        method = api_config["method"]

        if method == "GET":
            request_param_template = api_config["request_params"]
        elif method == "POST":
            request_param_template = api_config["request_body"]
        params = {
            "platform_authorization": platform_authorization,
            "module_name": system_code,
            "action": action,
            "base_url": base_url,
            "method": method,
            "request_param_template": request_param_template,
            "request_context": request_context,
        }

        return RequestApiConfigResource()(params)
