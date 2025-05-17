from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy
from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE

from core.exceptions import CoreException


class BaseIAMError(CoreException):
    """权限中心异常 ."""

    MODULE_CODE = 99
    MESSAGE = _lazy("权限中心异常")


class ActionNotExistError(BaseIAMError):
    """动作ID不存在 ."""

    ERROR_CODE = "001"
    MESSAGE = _lazy("动作ID不存在")


class ResourceNotExistError(BaseIAMError):
    """资源ID不存在 ."""

    ERROR_CODE = "002"
    MESSAGE = _lazy("资源ID不存在")


class GetSystemInfoError(BaseIAMError):
    """获取系统信息错误 ."""

    ERROR_CODE = "003"
    MESSAGE = _lazy("获取系统信息错误")


class ResourceAttrTypeExists(BaseIAMError):
    """资源属性类型已存在 ."""

    ERROR_CODE = "004"
    MESSAGE = _lazy("资源属性类型已存在")


class ResourceAttrNameExists(BaseIAMError):
    """资源属性名称已存在 ."""

    ERROR_CODE = "005"
    MESSAGE = _lazy("资源属性名称已存在")


class ResourceAttrTypeNotExists(BaseIAMError):
    """资源属性类型{attr_type}不存在 ."""

    ERROR_CODE = "006"
    MESSAGE = _lazy("资源属性类型{attr_type}不存在")

    def __init__(self, *args, attr_type, data=None, **kwargs):
        # pylint: disable=invalid-name
        self.MESSAGE = self.MESSAGE.format(attr_type=attr_type)
        super().__init__(**kwargs)


class ResourceAttrTypeIsNotExists(BaseIAMError):
    """资源属性类型不能为空 ."""

    ERROR_CODE = "007"
    MESSAGE = _lazy("资源属性类型不能为空")


class ResourceTypeConfuse(BaseIAMError):
    """同一鉴权仅支持一种资源类型 ."""

    ERROR_CODE = "008"
    MESSAGE = _lazy("同一鉴权仅支持一种资源类型")


class ResourceTypeNumsConfuse(BaseIAMError):
    """鉴权操作与资源类型数量不一致 ."""

    ERROR_CODE = "009"
    MESSAGE = _lazy("鉴权操作与资源类型数量不一致")


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
