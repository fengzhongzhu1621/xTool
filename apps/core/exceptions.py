import json
import logging
from enum import Enum
from json.decoder import JSONDecodeError

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy as _lazy
from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from apps.core.constants import ErrorCode
from xTool.log import logger


def custom_exception_handler(exc, context):
    """
    分类：
        APIException及子类异常
        app自定义异常和未处理异常
    """
    response = exception_handler(exc, context)
    if response:
        return Response(
            response.data["detail"] if "detail" in response.data else response.data,
            status=response.status_code,
        )

    exc_message = str(exc)
    exc_data = None
    if hasattr(exc, "data") and exc.data:
        try:
            exc_data = exc.data if isinstance(exc.data, dict) else json.loads(exc.data)
        except JSONDecodeError:
            exc_data = exc.data
        except TypeError:
            # 其它内容不能被json解析 忽略
            pass

    if hasattr(exc, "message") and exc.message:
        try:
            exc_message = json.loads(str(exc.message))
        except JSONDecodeError:
            exc_message = str(exc.message)

    # 如果是权限异常，返回403
    error_code = (
        exc.code
        if isinstance(exc, AppException)
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    status_code = (
        status.HTTP_403_FORBIDDEN
        if isinstance(exc, PermissionDeniedError)
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    # 由前端处理无权限调整
    if exc_data and isinstance(exc_data, dict):
        error_code = exc_data.get("code", error_code)
        if error_code == ErrorCode.IAM_NOT_PERMISSION.value:
            exc_data = {
                "apply_url": exc_data.get("apply_url")
                or exc_data.get("data", {}).get("apply_url"),
                "permission": exc_data.get("permission")
                or exc_data.get("data", {}).get("permission"),
            }
            status_code = status.HTTP_403_FORBIDDEN

    data = {
        "code": error_code,
        "message": exc_message,
        "data": exc_data,
    }

    # 使用json方便提取
    logger.exception(json.dumps(data, cls=DjangoJSONEncoder))
    return Response(data, status=status_code)


class AppException(Exception):

    PLATFORM_CODE = getattr(settings, "PLATFORM_CODE", "00")
    MODULE_CODE = "00"
    ERROR_CODE = "500"
    MESSAGE = _("APP异常")
    STATUS_CODE = 500
    LOG_LEVEL = logging.ERROR

    def __init__(self, *args, message=None, data=None, **kwargs):
        super().__init__(*args)

        if len(self.ERROR_CODE) == 3:
            code = f"{self.PLATFORM_CODE}{self.MODULE_CODE}{self.ERROR_CODE}"
        else:
            # 兼容旧版ERROR_CODE异常码长度不为3位 -> 只组合平台码和异常码
            code = f"{self.PLATFORM_CODE}{self.ERROR_CODE}"

        self.code = code
        self.errors = kwargs.get("errors")
        # 优先使用第三方系统的错误编码
        if kwargs.get("code"):
            self.code = kwargs["code"]

        self.message = force_text(message) if message else force_text(self.MESSAGE)

        self.data = data


class ClientException(AppException):
    """
    客户端请求异常
    """

    MESSAGE = _("客户端请求异常")
    ERROR_CODE = "400"
    STATUS_CODE = 400


class ParamValidationError(ClientException):
    """
    客户端异常：参数验证失败
    """

    MESSAGE = _("参数验证失败")
    ERROR_CODE = "400"
    STATUS_CODE = 400


class CoreException(AppException):
    PLATFORM_CODE = settings.PLATFORM_CODE
    MODULE_CODE = "01"

    class Modules(object):
        META = "01"
        ACCOUNT = "02"


class BaseIAMError(CoreException):
    """权限中心异常 ."""

    MODULE_CODE = 99  # 蓝鲸体系通用服务错误码
    MESSAGE = _lazy("权限中心异常")


class PermissionDeniedError(BaseIAMError):
    """权限校验不通过 ."""

    ERROR_CODE = "403"
    MESSAGE = _lazy("权限校验不通过")

    def __init__(self, action_name, permission, apply_url=settings.BK_IAM_SAAS_HOST):
        message = _("当前用户无 [{action_name}] 权限").format(action_name=action_name)
        data = {
            "permission": permission,
            "apply_url": apply_url,
        }
        super().__init__(message, data=data, code=HTTP_AUTH_FORBIDDEN_CODE)
