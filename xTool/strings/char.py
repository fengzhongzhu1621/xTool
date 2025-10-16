from typing import List


def get_chr_seq(begin_chr: str, end_chr: str) -> List[str]:
    """
    生成从 begin_chr 到 end_chr 的字符序列（包含 end_chr）

    :param begin_chr: 起始字符（如 'a'）
    :param end_chr: 结束字符（如 'z'）
    :return: 包含从 begin_chr 到 end_chr 所有字符的列表（如 ['a', 'b', ..., 'z']）
    """
    return [chr(ascii_int) for ascii_int in range(ord(begin_chr), ord(end_chr) + 1)]
