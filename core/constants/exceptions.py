from enum import Enum, unique

from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE


@unique
class ErrorCode(Enum):
    """
    ESB异常代码
    """

    ESB_API_NOT_FORBIDDEN = 20102  # API没有权限
    ESB_API_FORMAT_ERROR = 1306201  # API后端返回格式异常
    IAM_NOT_PERMISSION = HTTP_AUTH_FORBIDDEN_CODE
