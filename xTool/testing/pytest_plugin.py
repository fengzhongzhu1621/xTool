import asyncio
from pathlib import Path
from typing import List

import pytest

from xTool.testing.testing import loop_context


@pytest.fixture
def loop(loop_factory, fast, loop_debug):  # type: ignore
    """Return an instance of the event loop."""
    policy = loop_factory()
    asyncio.set_event_loop_policy(policy)
    with loop_context(fast=fast) as _loop:
        if loop_debug:
            _loop.set_debug(True)  # pragma: no cover
        asyncio.set_event_loop(_loop)
        yield _loop


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
