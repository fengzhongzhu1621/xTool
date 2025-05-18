from django.utils.translation import gettext_lazy as _lazy

from xTool.exceptions import XToolException


class RSAEncryptException(XToolException):
    MESSAGE = _lazy("密码加密失败")


class RSADecryptException(XToolException):
    MESSAGE = _lazy("密码解密失败")
