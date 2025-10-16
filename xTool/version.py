import re

version = "0.2.0"


def get_version_parsed_list(version):
    """返回日志版本解析结果"""
    # 返回一个整数列表，表示版本号的各个部分（如 [1, 2, 3] 对应 v1.2.3）。
    log_version_pattern = re.compile(r"(\d+)")  # noqa
    return [int(value) for value in re.findall(log_version_pattern, version)]


def is_later_version(version1, version2):
    """判断version1版本号是否大于version2, None属于最旧的级别"""
    if version1 is None:
        return False
    if version2 is None:
        return True
    version1_values = get_version_parsed_list(version1)
    version2_values = get_version_parsed_list(version2)
    return version1_values > version2_values
