# -*- coding: utf-8 -*-

try:
    from collections import UserDict
except ImportError:
    pass
from typing import Any


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
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
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


# based on http://stackoverflow.com/a/2082169/151401
class CaseInsensitiveDict(dict):
    """ A case-insensitive dictionary for header storage.
        A limitation of this approach is the inability to store
        multiple instances of the same header. If that is changed
        then we suddenly care about the assembly rules in sec 2.3.
    """

    def __init__(self, d=None, **kwargs):
        super(CaseInsensitiveDict, self).__init__(**kwargs)
        if d:
            self.update((k.lower(), v) for k, v in d.items())

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())

    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(key.lower())


class ConstantDict(dict):
    """常量字典，不允许修改value值 ."""
    def __setitem__(self, key: Any, value: Any):
        raise TypeError("modifying %s object values is not allowed"
                        % self.__class__.__name__)
