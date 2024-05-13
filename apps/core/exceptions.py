import json
import logging
from json.decoder import JSONDecodeError
from typing import Dict

from bk_resource.exceptions import CoreException
from blueapps.core.exceptions import BlueException
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _lazy
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import exception_handler

try:
    from raven.contrib.django.raven_compat.models import sentry_exception_handler
except ImportError:
    sentry_exception_handler = None

from apps.core.constants import ErrorCode
from xTool.log import logger


def notify_sentry(request: Request, response: Response, data: Dict, exc: Exception):
    """通知 sentry"""
    if response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR:
        return
    if isinstance(exc, (BlueException, CoreException, ValidationError)):
        return
    # notify sentry
    if settings.RUN_MODE in ["PRODUCT", "STAGING"] and sentry_exception_handler is not None:
        sentry_exception_handler(request=request)


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
    error_code = exc.code if isinstance(exc, AppException) else status.HTTP_500_INTERNAL_SERVER_ERROR
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    # 由前端处理无权限调整
    if exc_data and isinstance(exc_data, dict):
        error_code = exc_data.get("code", error_code)
        if error_code == ErrorCode.IAM_NOT_PERMISSION.value:
            exc_data = {
                "apply_url": exc_data.get("apply_url") or exc_data.get("data", {}).get("apply_url"),
                "permission": exc_data.get("permission") or exc_data.get("data", {}).get("permission"),
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


class ApiError(BlueException):
    pass


class ValidationError(BlueException):
    MESSAGE = _lazy("参数验证失败")
    ERROR_CODE = "001"

    def __init__(self, *args, data=None, **kwargs):
        if args:
            custom_message = args[0]
            if isinstance(custom_message, tuple):
                super().__init__(custom_message[1], data=custom_message[0], **kwargs)
            else:
                super().__init__(custom_message, **kwargs)
        else:
            super().__init__(**kwargs)


class ApiResultError(ApiError):
    MESSAGE = _lazy("远程服务请求结果异常")
    ERROR_CODE = "002"


class ComponentCallError(BlueException):
    MESSAGE = _lazy("组件调用异常")
    ERROR_CODE = "003"


class LocalError(BlueException):
    MESSAGE = _lazy("组件调用异常")
    ERROR_CODE = "004"


class LanguageDoseNotSupported(BlueException):
    MESSAGE = _lazy("语言不支持")
    ERROR_CODE = "005"


class InstanceNotFound(BlueException):
    MESSAGE = _lazy("资源实例获取失败")
    ERROR_CODE = "006"


class PermissionError(BlueException):
    MESSAGE = _lazy("权限不足")
    ERROR_CODE = "403"


class ApiRequestError(ApiError):
    MESSAGE = _lazy("服务不稳定，请检查组件健康状况")
    ERROR_CODE = "015"


class AppException(Exception):
    PLATFORM_CODE = getattr(settings, "PLATFORM_CODE", "00")
    MODULE_CODE = "00"
    ERROR_CODE = "500"
    MESSAGE = _lazy("APP异常")
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

        self.message = force_str(message) if message else force_str(self.MESSAGE)

        self.data = data


class ClientException(AppException):
    """
    客户端请求异常
    """

    MESSAGE = _lazy("客户端请求异常")
    ERROR_CODE = "400"
    STATUS_CODE = 400


class ParamValidationError(ClientException):
    """
    客户端异常：参数验证失败
    """

    MESSAGE = _lazy("参数验证失败")
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
