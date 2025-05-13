import json
import os
import sys
import traceback
from json.decoder import JSONDecodeError
from typing import Dict

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.logger import logger
from core.exceptions import BlueException
from core.iam.exceptions import PermissionDeniedError

try:
    from raven.contrib.django.raven_compat.models import sentry_exception_handler
except ImportError:
    sentry_exception_handler = None
from core.constants import ErrorCode
from core.exceptions import CoreException


def notify_sentry(request: Request, response: Response, data: Dict, exc: Exception):
    """通知 sentry"""
    if response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR:
        return
    if isinstance(exc, (BlueException, CoreException, ValidationError)):
        return
    # notify sentry
    logger.error(
        """uncaught exception: [%s], request url: [%s], """
        """request method: [%s], request params: [%s], """
        """response data->[%s]"""
        % (
            traceback.format_exc(),
            request.path,
            request.method,
            json.dumps(getattr(request, request.method, None)),
            json.dumps(data, cls=DjangoJSONEncoder),
        )
    )
    if settings.RUN_MODE in ["PRODUCT", "STAGING"] and sentry_exception_handler is not None:
        sentry_exception_handler(request=request)


def custom_exception_handler(exc, context: Dict):
    """
    分类：
        APIException及子类异常
        app自定义异常和未处理异常
    """
    request = context["request"]
    response = exception_handler(exc, context)
    if response:
        data = response.data["detail"] if "detail" in response.data else response.data
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            notify_sentry(request, response, data, exc)
        return Response(data, status=response.status_code)

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
    error_code = exc.code if isinstance(exc, BlueException) else status.HTTP_500_INTERNAL_SERVER_ERROR
    status_code = (
        status.HTTP_403_FORBIDDEN if isinstance(exc, PermissionDeniedError) else status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    # 由前端处理无权限调整
    if exc_data and isinstance(exc_data, dict):
        error_code = exc_data.get("code", error_code)
        if error_code == ErrorCode.IAM_NOT_PERMISSION.value:
            exc_data = {
                "apply_url": exc_data.get("apply_url") or exc_data.get("data", {}).get("apply_url"),
                "permission": exc_data.get("permission") or exc_data.get("data", {}).get("permission"),
            }
            status_code = status.HTTP_403_FORBIDDEN

    # 使用json方便提取
    data = {
        "code": error_code,
        "message": exc_message,
        "data": exc_data,
    }

    # 追加 traceback
    if settings.DEBUG_RETURN_EXCEPTION:
        err_message = os.linesep.join(
            info.replace(settings.SECRET_KEY, "**********") for info in traceback.format_exception(*sys.exc_info())
        )
        data["error"] = err_message

    # 构造响应
    response = Response(data, status=status_code)

    # 通知 sentry
    notify_sentry(request, response, data, exc)

    return response
