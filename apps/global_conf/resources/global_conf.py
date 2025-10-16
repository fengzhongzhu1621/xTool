from enum import EnumMeta
from typing import Dict

from django.utils.translation import gettext_lazy as _lazy

from xTool.utils import ChoicesMeta, list_registered_choices

from .base import GlobalConfBaseResource


class GetGlobalConfResource(GlobalConfBaseResource):
    name = _lazy("获取全局配置")

    def perform_request(self, validated_request_data: Dict) -> Dict:
        choices = self.fetch_registered_choices()
        return choices

    @staticmethod
    def fetch_registered_choices():
        """获得所有注册的枚举 ."""
        # 获得注册的枚举配置
        result = {}
        for name, choices_enum in list_registered_choices().items():
            if isinstance(choices_enum, (EnumMeta, ChoicesMeta)):
                a = choices_enum.choices
                result[name] = [{"id": key, "name": label} for key, label in choices_enum.choices]

        return result
