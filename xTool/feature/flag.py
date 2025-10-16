from typing import Dict, List, Tuple

from .flag_field import FeatureFlagField
from .metaclass import FeatureFlagMeta

__all__ = ['FeatureFlag']


class FeatureFlag(str, metaclass=FeatureFlagMeta):
    """通过继承 str，FeatureFlag 的实例将表现得像字符串，同时可以附加额外的功能（如字段验证和管理） ."""

    def __new__(cls, value: str):
        """Cast a string into a predefined feature flag."""
        # 获取所有预定义的 FeatureFlagField 属性类实例
        for field in cls._get_feature_fields_().values():
            if field.name == value:
                # 将字符串值转换为预定义的 FeatureFlag 实例
                return value
        # 无效值校验
        return cls._missing_(value)

    @classmethod
    def _missing_(cls, value) -> str:
        raise ValueError("{!r} is not a valid {}".format(value, cls.__name__))

    @classmethod
    def get_default_flags(cls) -> Dict[str, bool]:
        """Get the default user feature flags, client is safe to modify the result because it's a copy"""
        features = {field.name: field.default for field in cls._get_feature_fields_().values()}
        # 以确保客户端代码可以安全地修改返回的字典而不会影响原始数据。
        return features.copy()

    @classmethod
    def get_django_choices(cls) -> List[Tuple[str, str]]:
        """Get Django-Like Choices for this FeatureFlag Collection."""
        return [(field.name, field.label) for field in cls._get_feature_fields_().values()]

    @classmethod
    def get_feature_label(cls, feature: str) -> str:
        """Get the label of provided feature flag"""
        return cls._get_feature_fields_()[cls(feature)].label

    @classmethod
    def register_feature_flag(cls, field: FeatureFlagField):
        """注册额外的FeatureFlagField"""
        name = field.name
        if cls._feature_flag_fields_.get(name, field).label != field.label:
            raise ValueError("Two Feature Flags cannot be set to the same value.")
        if not name:
            raise ValueError("Feature flag's name can not be empty.")

        cls._feature_flag_fields_[name] = field
        setattr(cls, name, field)
