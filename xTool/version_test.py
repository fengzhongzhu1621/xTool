from xTool.version import get_version_parsed_list, is_later_version


def test_get_version_parsed_list():
    assert get_version_parsed_list("v1.2.3") == [1, 2, 3]
    assert get_version_parsed_list("2.0.1") == [2, 0, 1]
    assert get_version_parsed_list("v3.14.159") == [3, 14, 159]


def test_is_later_version():
    assert is_later_version("v1.2.3", "v1.2.2") is True
    assert is_later_version("v1.2.3", "v1.2.3") is False
    assert is_later_version("v1.2.3", "v1.2.4") is False
