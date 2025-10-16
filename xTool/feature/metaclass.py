from typing import Dict

from .flag_field import FeatureFlagField

__all__ = ['FeatureFlagMeta']


class FeatureFlagMeta(type):
    """定义一个名为 FeatureFlagMeta 的元类，继承自内置的 type 类。元类用于自定义类的创建过程，允许你在类定义时插入自定义逻辑。

    元类用于管理 FeatureFlag 类中的 FeatureFlagField 描述符。
    它负责收集、验证和存储所有的 FeatureFlagField 实例。
    """

    # 存储所有 FeatureFlagField 描述符实例，以便后续访问和管理
    _feature_flag_fields_: Dict[str, FeatureFlagField]

    def __new__(mcs, cls_name: str, bases, dct: Dict):
        """__new__ 是一个特殊方法，在创建类的实例（这里是类本身）时调用。

        :param mcs:（通常命名为 cls，但这里用 mcs 表示“元类自身”）：当前的元类，即 FeatureFlagMeta。
        :param cls_name: 即将创建的类的名称（字符串）
        :param bases: 即将创建的类的基类（父类）的元组
        :param dct: 即将创建的类的命名空间字典，包含类属性和方法
        """
        fields = {}
        # 遍历所有基类（父类）
        for base in bases:
            # 对于每个基类，尝试获取其 _feature_flag_fields_ 属性。如果存在，则将其内容合并到当前的 _feature_flag_fields_ 字典中。
            fields.update(getattr(base, "_feature_flag_fields_", {}))

        # 遍历类的命名空间字典 dct 中的所有属性和值。
        for attr, field in dct.items():
            if not isinstance(field, FeatureFlagField):
                continue

            # 比较获取到的 label 和当前 field.label 是否相同
            if fields.get(attr, field).label != field.label:
                raise ValueError("Two Feature Flags cannot be set to the same value.")
            if not attr:
                raise ValueError("Feature flag's name can not be empty.")

            fields[attr] = field

        # 添加到类的命名空间
        # 在类创建完成后，可以通过 cls._feature_flag_fields_ 访问所有 FeatureFlagField 实例
        dct["_feature_flag_fields_"] = fields
        return super().__new__(mcs, cls_name, bases, dct)

    def _get_feature_fields_(cls) -> Dict[str, FeatureFlagField]:
        return cls._feature_flag_fields_

    def __iter__(cls):
        yield from cls._get_feature_fields_()
