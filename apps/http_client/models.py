from typing import Dict

from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import (
    EMPTY_STRING,
    LEN_LONG,
    LEN_NORMAL,
    LEN_SHORT,
    LEN_X_LONG,
    LEN_XX_LONG,
    RequestMethod,
)
from core.models import SoftDeleteModel


class RequestSystemConfig(SoftDeleteModel):
    name = models.CharField(_lazy("系统名称"), max_length=LEN_NORMAL, null=False)
    code = models.CharField(_lazy("API编码"), max_length=LEN_NORMAL, null=False, db_index=True, default="")
    desc = models.CharField(_lazy("系统描述"), max_length=LEN_LONG, default=EMPTY_STRING, null=True, blank=True)
    owners = models.CharField(_lazy("系统责任人"), max_length=LEN_NORMAL, default=EMPTY_STRING, null=True, blank=True)
    domain = models.CharField(_lazy("系统域名"), max_length=LEN_XX_LONG, default=EMPTY_STRING, null=True, blank=True)
    headers = models.JSONField(_lazy("系统公共头部"), default=list, null=True, blank=True)

    class Meta:
        app_label = "http_client"
        verbose_name = _lazy("系统配置")
        verbose_name_plural = _lazy("系统配置")
        unique_together = ("code",)


class RequestApiConfig(SoftDeleteModel):
    system = models.ForeignKey(
        RequestSystemConfig, db_constraint=False, on_delete=models.CASCADE, help_text=_lazy("系统")
    )
    code = models.CharField(_lazy("API编码"), max_length=LEN_NORMAL, null=False, db_index=True, default="")
    name = models.CharField(_lazy("API名称"), max_length=LEN_NORMAL, null=False)
    path = models.CharField(_lazy("API路径"), max_length=LEN_X_LONG, null=False)
    method = models.CharField(_lazy("请求方法"), max_length=LEN_SHORT, choices=[("GET", "GET"), ("POST", "POST")])
    desc = models.CharField(_lazy("描述"), max_length=LEN_LONG, default="")
    request_headers = models.JSONField(_lazy("headers参数"), default=list, null=True, blank=True)
    request_params = models.JSONField(_lazy("query参数"), default=list, null=True, blank=True)
    request_body = models.JSONField(_lazy("body参数"), default=dict, null=True, blank=True)

    class Meta:
        app_label = "http_client"
        verbose_name = _lazy("API配置")
        verbose_name_plural = _lazy("API配置")
        unique_together = ("code", "system")

    def to_json(self) -> Dict:
        result = {
            "system": {
                "domain": self.system.domain,
                "code": self.system.code,
            },
            "code": self.code,
            "path": self.path,
            "method": self.method,
            "request_params": self.request_params,
            "request_body": self.request_body,
            "request_headers": self.request_headers,
        }

        return result


class ApiWhiteList(SoftDeleteModel):
    url = models.CharField(max_length=LEN_SHORT, verbose_name=_lazy("url地址"))
    method = models.CharField(
        max_length=LEN_SHORT,
        default=RequestMethod.GET.value,
        choices=RequestMethod.choices,
        verbose_name=_lazy("接口请求方法"),
        null=True,
        blank=True,
    )
    enable_datasource = models.BooleanField(default=True, verbose_name=_lazy("激活数据权限"), blank=True)

    class Meta:
        verbose_name = _lazy("接口白名单")
        verbose_name_plural = verbose_name
