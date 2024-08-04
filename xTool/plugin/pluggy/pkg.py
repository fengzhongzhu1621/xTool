import importlib


class DistFacade:
    """Emulate a pkg_resources Distribution

    可用于在不直接依赖 pkg_resources 的情况下处理 Python 包的元数据。
    这使得代码更具可移植性，尤其是在处理不同版本的 setuptools 和 pkg_resources 时。
    """

    def __init__(self, dist: importlib.metadata.Distribution) -> None:
        self._dist = dist

    @property
    def project_name(self) -> str:
        name: str = self.metadata["name"]
        return name

    def __getattr__(self, attr: str, default=None):
        return getattr(self._dist, attr, default)

    def __dir__(self) -> list[str]:
        """返回一个列表，包含 self._dist 的所有属性，以及 DistFacade 类的内部变量（_dist）和项目名称属性（project_name）。
        这有助于在使用 dir() 函数时提供更完整的属性列表。"""
        return sorted(dir(self._dist) + ["_dist", "project_name"])
