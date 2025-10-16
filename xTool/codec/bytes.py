def tob(s, enc="utf-8"):
    """将字符串转换为utf8/bytes编码 ."""
    return s.encode(enc) if not isinstance(s, bytes) else s


def tou(s, enc="utf-8"):
    """将字符串转换为unicode编码 ."""
    return s.decode(enc) if isinstance(s, bytes) else s
