from core.feature import FeatureFlagField


class FeatureFlag:
    dark_mode = FeatureFlagField(label="Enable dark mode", default=False)
    # 等价于：
    # dark_mode = FeatureFlagField(name="dark_mode", label="Enable dark mode", default=False)


def test_flag_field():
    assert FeatureFlag.dark_mode == "dark_mode"
