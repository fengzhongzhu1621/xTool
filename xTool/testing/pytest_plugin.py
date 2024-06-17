from pathlib import Path
from typing import List


def append_pytest_fixture_plugins(root_path: Path, path: Path) -> List[str]:
    """添加额外的 fixtures"""

    def refactor(_path: str) -> str:
        return _path.strip("/").strip("\\").replace("/", ".").replace("\\", ".").replace(".py", "")

    paths = []
    prefix = str(root_path)
    prefix_len = len(prefix)

    # 递归遍历目录下所有文件
    for path in path.iterdir():
        if not path.is_file():
            continue
        filename = path.name
        # 去掉 __init_.py
        if filename.startswith("__"):
            continue
        # 过滤掉非 python 文件
        if filename.endswith(".py"):
            paths.append(refactor(str(path)[prefix_len:]))

    return paths
