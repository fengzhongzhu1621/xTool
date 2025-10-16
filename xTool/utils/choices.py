import enum
from typing import Callable

__all__ = [
    "ChoicesMeta",
    "Choices",
    "IntegerChoices",
    "TextChoices",
    "register_choices",
    "list_registered_choices",
]


class ChoicesMeta(enum.EnumMeta):
    """A metaclass for creating a enum choices."""

    def __new__(metacls, classname, bases, classdict, **kwds):
        labels = []
        for key in classdict._member_names:
            value = classdict[key]
            if isinstance(value, (list, tuple)) and len(value) > 1 and isinstance(value[-1], str):
                *value, label = value
                value = tuple(value)
            else:
                label = key.replace("_", " ").title()
            labels.append(label)
            # Use dict.__setitem__() to suppress defenses against double
            # assignment in enum's classdict.
            dict.__setitem__(classdict, key, value)
        cls = super().__new__(metacls, classname, bases, classdict, **kwds)
        cls._value2label_map_ = dict(zip(cls._value2member_map_, labels))
        # Add a label property to instances of enum which uses the enum member
        # that is passed in as "self" as the value to use when looking up the
        # label in the choices.
        cls.label = property(lambda self: cls._value2label_map_.get(self.value))
        cls.do_not_call_in_templates = True
        return enum.unique(cls)

    def __contains__(cls, member):
        if not isinstance(member, enum.Enum):
            # Allow non-enums to match against member values.
            return any(x.value == member for x in cls)
        return super().__contains__(member)

    @property
    def names(cls):
        empty = ["__empty__"] if hasattr(cls, "__empty__") else []
        return empty + [member.name for member in cls]

    @property
    def choices(cls):
        empty = [(None, cls.__empty__)] if hasattr(cls, "__empty__") else []
        return empty + [(member.value, member.label) for member in cls]

    @property
    def labels(cls):
        return [label for _, label in cls.choices]

    @property
    def values(cls):
        return [value for value, _ in cls.choices]


class Choices(enum.Enum, metaclass=ChoicesMeta):
    """Class for creating enumerated choices."""

    def __str__(self):
        """
        Use value when cast to str, so that Choices set as model instance
        attributes are rendered as expected in templates and similar contexts.
        """
        return str(self.value)


class IntegerChoices(int, Choices):
    """Class for creating enumerated integer choices."""

    pass


class TextChoices(str, Choices):
    """Class for creating enumerated string choices."""

    def _generate_next_value_(name, start, count, last_values):
        return name


# 存放已注册的枚举类
_default = {}


def register_choices(name: str) -> Callable:
    """
    注册choices类型的配置
    """

    def decorator(cls):
        nonlocal name
        # 如果装饰的为类，则取类名
        if not name:
            name = cls.__name__
        # 将列表转换为Enum类型
        if isinstance(cls, list):
            cls = enum.Enum(name, names=cls)

        _default[name] = cls
        return cls

    return decorator


def list_registered_choices():
    """获得已经注册的所有choicesEnum ."""
    return _default
