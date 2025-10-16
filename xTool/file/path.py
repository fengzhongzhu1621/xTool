import os


def path_to_dotted(path: str, sep=None) -> str:
    """将路径转换为 . 分隔的格式 ."""
    if not sep:
        sep = os.sep
    return ".".join(path_item for path_item in path.split(sep) if path_item)
