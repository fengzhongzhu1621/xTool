TRANSFORM_TAB = str.maketrans({"\n": r"\n", "\r": r"\r", "\t": r"\t"})


def transform_escape_char(value: str) -> str:
    """转义字符串 ."""
    return value.translate(TRANSFORM_TAB)
