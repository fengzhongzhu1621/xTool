"""
Tracing utils
"""

from __future__ import annotations

from typing import Any, Callable, Sequence, Tuple

# 一个接受字符串并返回任意对象的函数类型。
_Writer = Callable[[str], object]
# 一个接受标签元组和参数元组，并返回任意对象的函数类型。
_Processor = Callable[[Tuple[str, ...], Tuple[Any, ...]], object]


class TagTracer:
    """标签管理器，用于管理标签处理器和写入器 ."""

    def __init__(self) -> None:
        # 标签元组和标签处理器的映射关系
        self._tags2proc: dict[tuple[str, ...], _Processor] = {}
        self._writer: _Writer | None = None
        self.indent = 0

    def get(self, name: str) -> TagTracerSub:
        """创建一个子标签，该实例与当前 TagTracer 关联，并添加一个新的标签 ."""
        return TagTracerSub(self, (name,))

    def _format_message(self, tags: Sequence[str], args: Sequence[object]) -> str:
        if isinstance(args[-1], dict):
            extra = args[-1]
            args = args[:-1]
        else:
            extra = {}

        content = " ".join(map(str, args))
        indent = "  " * self.indent

        # 多个标签用 : 分割
        lines = ["{}{} [{}]\n".format(indent, content, ":".join(tags))]

        for name, value in extra.items():
            lines.append(f"{indent}    {name}: {value}\n")

        return "".join(lines)

    def _process_message(self, tags: tuple[str, ...], args: tuple[object, ...]) -> None:
        # 执行标签写入
        if self._writer is not None and args:
            self._writer(self._format_message(tags, args))
        # 处理标签
        try:
            processor = self._tags2proc[tags]
        except KeyError:
            pass
        else:
            processor(tags, args)

    def set_writer(self, writer: _Writer | None) -> None:
        """设置写入器 ."""
        self._writer = writer

    def set_processor(self, tags: str | tuple[str, ...], processor: _Processor) -> None:
        """设置特定标签的处理器 ."""
        # 将标签转换为元组格式
        if isinstance(tags, str):
            tags = tuple(tags.split(":"))
        else:
            assert isinstance(tags, tuple)
        self._tags2proc[tags] = processor


class TagTracerSub:
    """子标签管理器：用于简化标签的使用 ."""

    def __init__(self, root: TagTracer, tags: tuple[str, ...]) -> None:
        self.root = root
        self.tags = tags

    def __call__(self, *args: object) -> None:
        self.root._process_message(self.tags, args)

    def get(self, name: str) -> TagTracerSub:
        """返回一个新的 TagTracerSub 实例，该实例与当前 TagTracerSub 关联，并添加一个新的标签。"""
        return self.__class__(self.root, self.tags + (name,))
