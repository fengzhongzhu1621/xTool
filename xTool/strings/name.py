import re


def name_handler(name: str, max_length: int) -> str:
    """去掉字符串中的特殊字符 ."""
    # 使用正则表达式去除字符串中的特定特殊字符（包括.<>.,;~!@#^&*￥'"\这些字符）
    name_str = re.compile(r'[<>.,;~!@#^&*￥\'\"]+').sub('', name)
    # 将处理后的字符串截断至最多max_length个字符的长度。
    return name_str[:max_length]
