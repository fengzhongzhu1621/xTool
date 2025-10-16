from collections import OrderedDict
from enum import Enum as OrigEnum
from enum import EnumMeta, auto
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

if TYPE_CHECKING:
    EnumFieldBase = Any
else:
    EnumFieldBase = object

__all__ = [
    'StructuredEnum',
]


class EnumField(EnumFieldBase):
    """Use it with `StructuredEnum` type

    :param real_value: the real value of enum member
    :param label: the label text of current enum value
    :param is_reserved: if current member was reserved, it will not be included in choices
    """

    def __init__(self, real_value: Any, label: Optional[str] = None, is_reserved: bool = False):
        # 枚举成员的实际值，可以是任意类型。
        self.real_value = real_value
        # 当前枚举值的标签文本，用于显示或描述。
        self.label = label
        # 布尔值，指示当前成员是否被保留。如果被保留，则不会包含在 choices 中。
        self.is_reserved = is_reserved

    def set_label_if_empty(self, key: str):
        """Set field's label if not provided 在 label 未提供时自动生成一个标签

        1. 转换为小写  ：key.lower() 将 key 中的所有字符转换为小写。
        2. 替换下划线为空格  ：.replace("_", " ") 将所有下划线 _ 替换为空格  。
        3. 首字母大写  ：.capitalize() 将字符串的第一个字符转换为大写，其余字符转换为小写。
        """
        if not self.label:
            self.label = key.lower().replace("_", " ").capitalize()


class StructuredEnumMeta(EnumMeta):
    """The metaclass of StructuredEnum

    EnumMeta 是 Python 内置的枚举元类，用于控制枚举类的创建过程。
    """

    # 存储与枚举类相关的字段成员信息。
    __field_members__: Dict[Type, Dict]

    def __new__(metacls, cls, bases, classdict):
        field_members = metacls.process_enum_fields(classdict)
        classdict["__field_members__"] = field_members
        return super().__new__(metacls, cls, bases, classdict)

    @staticmethod
    def process_enum_fields(classdict) -> Dict:
        """Iterate all enum members, transform them into `EnumField` objects and return as a dict.

        `EnumField` members in `classdict` will be replaced with their `real_value` attribute so `EnumMeta` can
        continue the initialization.

        处理 classdict 中的枚举字段，将其转换为 EnumField 对象，并返回一个包含这些字段的字典。
        """
        fields = OrderedDict()
        # Find out all `EnumField` instance, store them into class so we can use them later
        # 遍历 classdict 中的所有键值对，其中 key 是枚举成员的名称，member 是对应的值。
        for key, member in classdict.items():
            # Ignore all private members
            # 忽略私有成员
            if key.startswith("_"):
                continue

            # Turn regular enum member into EnumField instance
            # 如果当前成员不是 EnumField 实例，但是是 int, str 或 auto 类型，则将其转换为 EnumField 实例
            if not isinstance(member, EnumField) and isinstance(member, (int, str, auto)):
                member = EnumField(member)

            # 跳过非 EnumField 或被保留的成员
            if not isinstance(member, EnumField) or member.is_reserved:
                continue

            # 根据 key 自动生成一个标签
            member.set_label_if_empty(key)
            fields[key] = member

            # classdict 中的值替换为 EnumField 对象的 real_value 属性。
            # Use dict's setitem method because setting value with `classdict[key]` is forbidden
            dict.__setitem__(classdict, key, member.real_value)
        return fields

    def get_field_members(cls) -> Dict:
        return cls.__field_members__


class StructuredEnum(OrigEnum, metaclass=StructuredEnumMeta):
    """Structured Enum type, providing extra features such as getting enum members as choices tuple"""

    @classmethod
    def get_django_choices(cls) -> List[Tuple[Any, str]]:
        """Get Django-Like Choices for all field members."""
        return cls.get_choices()

    @classmethod
    def get_choice_label(cls, value: Any) -> str:
        """Get the label of field member by value"""
        if isinstance(value, cls):
            value = value.value

        members = cls.get_field_members()
        for field in members.values():
            if value == field.real_value:
                return field.label

        return value

    @classmethod
    def get_labels(cls) -> List[str]:
        """Get the label list for all field members."""
        return [item[1] for item in cls.get_choices()]

    @classmethod
    def get_values(cls) -> List[Any]:
        """Get the value list for all field members."""
        return [item[0] for item in cls.get_choices()]

    @classmethod
    def get_choices(cls) -> List[Tuple[Any, str]]:
        """Get Choices for all field members."""
        members = cls.get_field_members()
        return [(field.real_value, field.label) for field in members.values()]
