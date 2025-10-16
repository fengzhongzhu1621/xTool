import pytest

from apps.global_conf.register import GlobalConfig, GlobalConfigItem, register_global_config

pytestmark = pytest.mark.django_db


def test_get_key():
    @register_global_config
    class GlobalConfigExample:
        EXAMPLE_KEY_1 = GlobalConfigItem(value="hello", description="hello world!")

    assert GlobalConfig.objects.get_value("EXAMPLE_KEY_1") == "hello"
