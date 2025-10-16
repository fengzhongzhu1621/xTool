def is_consecutive_strings(str_list: list) -> bool:
    """
    判断字符串数字列表是否连续

    参数:
        str_list: 字符串数字列表，如 ["1", "2", "3"]

    返回:
        bool: 如果数字连续返回True，否则返回False

    示例:
        >>> is_consecutive_strings(["1", "2", "3"])
        True
        >>> is_consecutive_strings(["1", "3", "4"])
        False
    """
    if not str_list:  # 处理空列表情况
        return False

    try:
        # 转换为整数并去重排序
        int_sorted = sorted({int(s) for s in str_list})
    except ValueError:  # 处理非数字字符串
        return False

    if len(int_sorted) <= 1:  # 单个元素或空列表视为连续
        return True

    # 检查是否连续
    return int_sorted[-1] - int_sorted[0] == len(int_sorted) - 1
