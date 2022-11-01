# -*- coding: utf-8 -*-

from typing import List


def split_member_list(member_str: str, sep=',') -> List:
    """将字符串按指定分隔符分割 ."""
    if not member_str:
        return []
    members = [member.strip() for member in member_str.strip().split(sep) if member.strip()]
    return members
