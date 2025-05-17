import base64
from typing import Union


def base64_encode(content: Union[str, bytes]) -> str:
    """
    将字符串转为base64编码
    :param content: 待转换字符串
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    return base64.b64encode(content).decode("utf-8")


def base64_decode(content: Union[str, bytes]) -> str:
    """
    将base64编码的字符串转为原始字符串
    :param content: 待转换字符串
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    return base64.b64decode(content).decode("utf-8")
