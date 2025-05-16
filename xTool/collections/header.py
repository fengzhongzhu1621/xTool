from multidict import CIMultiDict  # type: ignore

__all__ = [
    'Header',
]


class Header(CIMultiDict):
    def get_all(self, key):
        return self.getall(key, default=[])
