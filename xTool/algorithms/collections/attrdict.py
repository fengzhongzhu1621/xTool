# -*- coding: utf-8 -*-

try:
    from collections import UserDict
except ImportError:
    pass


try:
    import typing  # noqa
    _ObjectDictBase = typing.Dict[str, typing.Any]
except ImportError:
    _ObjectDictBase = dict


class AttrDict(dict):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self[attr] = value

    def __iadd__(self, rhs):
        self.update(rhs)
        return self

    def __add__(self, rhs):
        d = AttrDict(self)
        d.update(rhs)
        return d


class ObjectDict(_ObjectDictBase):
    """Makes a dictionary behave like an object, with attribute-style access.
    """

    def __getattr__(self, name):
        # type: (str) -> Any
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        # type: (str, Any) -> None
        self[name] = value


class Row(dict):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class FancyDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)


class StripDict(UserDict):
    def __getitem__(self, key):
        if isinstance(key, str):
            key = key.strip()
        value = super().__getitem__(key)
        if value and isinstance(value, str):
            value = str(value).strip()
        return value
