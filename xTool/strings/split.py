from typing import List


def split_member_list(member_str: str, sep=",") -> List:
    """将字符串按指定分隔符分割 ."""
    if not member_str:
        return []
    members = [member.strip() for member in member_str.strip().split(sep) if member.strip()]
    return members


def split_str_to_list(string: str) -> List[str]:
    """
    把逗号、空格、换行符等分割字符串，转为数组
    eg: "a,b,c,d" -> ["a", "b", "c", "d"]
    :param string: 待分割字符串
    """
    string = string.strip()
    # 先把逗号、空格、换行符等分割字符串统一替换成 #####
    for char in [" ", "\n", "\t", "\r", "\f", "\v"]:
        string = string.replace(char, ",")
    return string.split(",")
