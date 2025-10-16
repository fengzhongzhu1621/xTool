import dataclasses

# @dataclasses.dataclass 是 Python 3.7+ 引入的一个装饰器，用于自动生成常见的特殊方法（如 __init__, __repr__, __eq__ 等），从而简化类的定义。

__all__ = [
    "FeatureFlagField",
]


@dataclasses.dataclass(init=False)
class FeatureFlagField:
    label: str
    default: bool
    name: str

    def __init__(self, name=None, label=None, default=False):
        """FeatureFlag 中的字段, 记录了 label、default 等属性，用于属性类

        :param label: 对这个 feature flag 的描述语句
        :param default: feature flag 的默认状态, 对于新引入的 feature flag, 该值建议为 False.
        :param name: 当前 Feature Flag 的名字, 当使用 register_ext_feature_flag 进行注册时, 必须提供该字段.
        """
        # 描述信息（如 "Enable dark mode"）。
        self.name = name or ""
        # 默认值（True/False）。
        self.label = label or name or ""
        # 开关名称（如 "dark_mode"）。
        self.default = default

    def __set_name__(self, owner, name):
        """自动将字段名注入 FeatureFlagField .

        利用描述符协议, 往 FeatureFlagField 注入 FeatureFlag 的名字.
        """
        self.name = name
        if not self.label:
            self.label = self.name

    def __get__(self, instance, owner):
        """返回 FeatureFlag 的名称. 因为 FeatureFlag 的值就是他自身的名称."""
        return self.name

    def __str__(self):
        return self.name
