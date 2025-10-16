import logging

from django.conf import settings
from django.utils.encoding import force_str
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy
from rest_framework import status


class BlueException(Exception):
    """
    异常统一封装类
    """

    PLATFORM_CODE = getattr(settings, "PLATFORM_CODE", "00")
    MODULE_CODE = "00"
    ERROR_CODE = "500"
    MESSAGE = _lazy("APP异常")
    STATUS_CODE = 500
    LOG_LEVEL = logging.ERROR

    def __init__(self, *args, message=None, data=None, **kwargs):
        """
        :param message: 错误消息
        :param data: 其他数据
        :param context: 错误消息 format dict
        :param args: 其他参数
        """
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

    def __str__(self):
        return "[{}] {}".format(self.code, self.message)

    def render_data(self):
        """
        返回异常信息
        """
        return self.data

    def response_data(self):
        """
        返回response数据
        """
        return {
            "result": False,
            "code": self.code,
            "message": self.message,
            "data": self.render_data(),
        }


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


class ClientBlueException(BlueException):
    """
    客户端请求异常
    """

    MESSAGE = _lazy("客户端请求异常")
    ERROR_CODE = "400"
    STATUS_CODE = 400


class ServerBlueException(BlueException):
    """
    服务器异常
    """

    MESSAGE = _lazy("服务端服务异常")
    ERROR_CODE = "500"
    STATUS_CODE = 500


class ResourceNotFound(ClientBlueException):
    """
    客户端异常：找不到请求的资源
    """

    MESSAGE = _lazy("找不到请求的资源")
    ERROR_CODE = "404"
    STATUS_CODE = 404


class ParamValidationError(ClientBlueException):
    """
    客户端异常：参数验证失败
    """

    MESSAGE = _lazy("参数验证失败")
    ERROR_CODE = "400"
    STATUS_CODE = 400


class ParamRequired(ClientBlueException):
    """
    客户端异常：关键参数缺失
    """

    MESSAGE = _lazy("关键参数缺失")
    ERROR_CODE = "401"
    STATUS_CODE = 400


class AccessForbidden(ClientBlueException):
    """
    客户端异常：登陆失败
    """

    MESSAGE = _lazy("登陆失败")
    ERROR_CODE = "413"
    STATUS_CODE = 403


class RequestForbidden(ClientBlueException):
    """
    客户端异常：请求拒绝
    """

    MESSAGE = _lazy("请求拒绝")
    ERROR_CODE = "423"
    STATUS_CODE = 403


class ResourceLock(ClientBlueException):
    """
    客户端异常：请求资源被锁定
    """

    MESSAGE = _lazy("请求资源被锁定")
    ERROR_CODE = "433"
    STATUS_CODE = 403


class MethodError(ClientBlueException):
    """
    客户端异常：请求方法不支持
    """

    MESSAGE = _lazy("请求方法不支持")
    ERROR_CODE = "405"
    STATUS_CODE = 405


class RioVerifyError(ClientBlueException):
    """
    客户端异常：智能网关检测失败
    """

    MESSAGE = _lazy("登陆请求经智能网关检测失败")
    ERROR_CODE = "415"
    STATUS_CODE = 405


class BkJwtVerifyError(ClientBlueException):
    """
    客户端异常：JWT检测失败
    """

    MESSAGE = _lazy("登陆请求经JWT检测失败")
    ERROR_CODE = "425"
    STATUS_CODE = 401


class DatabaseError(ServerBlueException):
    """
    服务端异常：数据库异常
    """

    MESSAGE = _lazy("数据库异常")
    ERROR_CODE = "501"


class ApiNetworkError(ServerBlueException):
    """
    服务端异常：网络异常
    """

    MESSAGE = _lazy("网络异常导致远程服务失效")
    ERROR_CODE = "503"
    STATUS_CODE = 503


class ApiResultError(ServerBlueException):
    """
    服务端异常：远程服务请求结果异常
    """

    MESSAGE = _lazy("远程服务请求结果异常")
    ERROR_CODE = "513"
    STATUS_CODE = 503


class ApiNotAcceptable(ServerBlueException):
    """
    服务端异常：远程服务返回结果格式异常
    """

    MESSAGE = _lazy("远程服务返回结果格式异常")
    ERROR_CODE = "523"
    STATUS_CODE = 503


class LocalError(ServerBlueException):
    """
    服务端异常：组件调用异常
    """

    MESSAGE = _lazy("组件调用异常")
    ERROR_CODE = "533"


class LockError(ServerBlueException):
    MESSAGE = _lazy("获取锁失败")
    ERROR_CODE = "543"


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

    class Modules:
        META = "01"
        ACCOUNT = "02"


class BaseIAMError(CoreException):
    """权限中心异常 ."""

    MODULE_CODE = 99
    MESSAGE = _lazy("权限中心异常")


class CoreException(Exception):
    code = 100
    status_code = 500
    default_detail = _lazy("服务异常")

    def __init__(self, message=None, data=None, code=None):
        """
        :param message: 错误信息
        :param data: 错误数据
        :param code: 错误码
        """
        if message is None:
            message = self.default_detail
        self.detail = message
        self.message = message

        if data is not None:
            self.data = data

        if code is not None:
            self.code = code

    def __str__(self):
        return str(self.message)


class APIRequestError(CoreException):
    code = 101
    message = _lazy("API请求错误")

    def __init__(self, module_name: str = "", url: str = "", status_code: int = None, result=None):
        """
        :param result: 错误消息
        """
        if not isinstance(result, dict):
            result = {"message": result}
        if status_code:
            self.status_code = status_code
        result.update({"module_name": module_name, "url": url})

        self.data = result
        self.message = result.get("message")


class CustomError(CoreException):
    code = 102
    message = _lazy("未知错误")


class DrfApiError(CoreException):
    code = 103
    message = _lazy("REST API返回错误")

    @staticmethod
    def drf_error_processor(detail):
        """
        将DRF ValidationError 错误信息转换为字符串
        """
        if isinstance(detail, str):
            return detail
        elif isinstance(detail, dict):
            for k, v in list(detail.items()):
                if v:
                    return DrfApiError.drf_error_processor(v)
            else:
                return ""
        elif isinstance(detail, list):
            for item in detail:
                if item:
                    return DrfApiError.drf_error_processor(item)
            else:
                return ""
        else:
            return _("错误消息解析错误")


class HTTP404Error(CoreException):
    code = 104
    status_code = 404
    message = _lazy("资源不存在")


class UserInfoMissing(CoreException):
    code = 105
    message = _lazy("缺少用户信息")


class PermissionException(CoreException):
    code = 106
    status_code = 403
    default_detail = _lazy("权限不足")


class ValidateException(CoreException):
    """校验失败"""

    code = 107
    default_detail = _lazy("数据校验失败")


class PlatformAuthParamsNotExist(CoreException):
    code = 108
    default_detail = _lazy("平台鉴权参数未配置")


class IAMNoPermission(BlueException):
    PLATFORM_CODE = "99"
    ERROR_CODE = "403"
    MESSAGE = _lazy("权限不足")
    STATUS_CODE = status.HTTP_403_FORBIDDEN
