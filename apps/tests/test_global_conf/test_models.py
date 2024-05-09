import pytest

from apps.global_conf.models import GlobalConfig

pytestmark = pytest.mark.django_db


class TestGlobalConfig:
    def test_set_value__int(self):
        GlobalConfig.objects.set_value("NAME_INT", 1)

        assert GlobalConfig.objects.get_value("NAME_INT") == 1
        assert GlobalConfig.objects.get_value("NAME_INT_2", 2) == 2

        GlobalConfig.objects.set_value("NAME_INT", 3)
        assert GlobalConfig.objects.get_value("NAME_INT", 4) == 3

    def test_set_value__float(self):
        GlobalConfig.objects.set_value("NAME_FLOAT", 0.11)

        assert GlobalConfig.objects.get_value("NAME_FLOAT") == 0.11
        assert GlobalConfig.objects.get_value("NAME_FLOAT_2", 0.22) == 0.22

        GlobalConfig.objects.set_value("NAME_FLOAT", 0.33)
        assert GlobalConfig.objects.get_value("NAME_FLOAT", 0.44) == 0.33

    def test_set_value__bool(self):
        GlobalConfig.objects.set_value("NAME_BOOL", True)

        assert GlobalConfig.objects.get_value("NAME_BOOL") is True
        assert GlobalConfig.objects.get_value("NAME_BOOL_2", False) is False

        GlobalConfig.objects.set_value("NAME_BOOL", False)
        assert GlobalConfig.objects.get_value("NAME_BOOL", True) is False

    def test_set_value__bool(self):
        GlobalConfig.objects.set_value("NAME_STRING", "hello")

        assert GlobalConfig.objects.get_value("NAME_STRING") == "hello"
        assert GlobalConfig.objects.get_value("NAME_STRING_2") is None

        GlobalConfig.objects.set_value("NAME_STRING", "hello world")
        assert GlobalConfig.objects.get_value("NAME_STRING", "world") == "hello world"

    def test_set_value__null(self):
        GlobalConfig.objects.set_value("NAME_NULL", None)

        assert GlobalConfig.objects.get_value("NAME_NULL") is None

    def test_set_value__list(self):
        GlobalConfig.objects.set_value("NAME_LIST", [1, "a"])

        assert GlobalConfig.objects.get_value("NAME_LIST") == [1, "a"]
        assert GlobalConfig.objects.get_value("NAME_LIST_2") is None

        GlobalConfig.objects.set_value("NAME_LIST", ["hello", "world"])
        assert GlobalConfig.objects.get_value("NAME_LIST", "world") == ["hello", "world"]

    def test_set_value__dict(self):
        GlobalConfig.objects.set_value("NAME_DICT", {"a": 1, "b": "c"})

        assert GlobalConfig.objects.get_value("NAME_DICT") == {"a": 1, "b": "c"}
        assert GlobalConfig.objects.get_value("NAME_DICT_2") is None

        GlobalConfig.objects.set_value("NAME_DICT", {"d": "e"})
        assert GlobalConfig.objects.get_value("NAME_DICT", "world") == {"d": "e"}
