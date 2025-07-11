import os

import pytest

from xTool import misc


def test_get_encodings():
    items = misc.get_encodings()
    items = list(items)
    assert "utf8" in items


def test_exception_to_string():
    try:
        1 / 0
    except Exception:  # noqa
        value = misc.exception_to_string()
        assert "ZeroDivisionError" in value


def test_get_cur_info():
    actual = misc.get_cur_info()
    value = ("test_get_cur_info", 35)
    assert value[0] == actual[0]


def test_run_command():
    misc.run_command("echo 1")


def test_get_run_command_result():
    actual = misc.get_run_command_result("echo 1")
    expect = (0, b"1" + misc.tob(os.linesep), b"")
    assert actual == expect


def test_is_memory_available():
    actual = misc.is_memory_available(limit=1)
    assert actual is False
    actual = misc.is_memory_available(limit=100)
    assert actual is True


def test_is_disk_available():
    actual = misc.is_disk_available(".", limit=1)
    assert actual is False
    actual = misc.is_disk_available(".", limit=100)
    assert actual is True


def test_grouper():
    n = 3
    iterable = "abcdefg"
    actual = misc.grouper(n, iterable, padvalue=None)
    expect = [("a", "b", "c"), ("d", "e", "f"), ("g", None, None)]
    assert list(actual) == expect
    actual = misc.grouper(n, iterable, padvalue="x")
    expect = [("a", "b", "c"), ("d", "e", "f"), ("g", "x", "x")]
    assert list(actual) == expect


def test_chunks():
    n = 3
    iterable = "abcdefg"
    actual = misc.chunks(iterable, n)
    assert list(actual) == ["abc", "def", "g"]


def test_chunked():
    n = 3
    iterable = "abcdefg"
    actual = misc.chunked(iterable, n)
    assert list(actual) == [["a", "b", "c"], ["d", "e", "f"], ["g"]]


def test_get_random_string():
    actual = misc.get_random_string(length=13)
    assert len(actual) == 13
    actual = misc.get_random_string(length=0)
    assert actual == ""


def test_strict_bool():
    with pytest.raises(ValueError):
        misc.strict_bool(True)
    with pytest.raises(ValueError):
        misc.strict_bool(False)
    with pytest.raises(ValueError):
        misc.strict_bool(None)
    with pytest.raises(ValueError):
        misc.strict_bool("None")
    assert misc.strict_bool("True") is True
    assert misc.strict_bool("False") is False
    with pytest.raises(ValueError):
        misc.strict_bool("true") is True
    with pytest.raises(ValueError):
        misc.strict_bool("false") is True


def test_less_strict_bool():
    with pytest.raises(ValueError):
        misc.less_strict_bool("abc")
    with pytest.raises(ValueError):
        misc.less_strict_bool("true") is True
    with pytest.raises(ValueError):
        misc.less_strict_bool("false") is True
    with pytest.raises(ValueError):
        misc.less_strict_bool("None")
    assert misc.less_strict_bool("True") is True
    assert misc.less_strict_bool("False") is False
    assert misc.less_strict_bool(True) is True
    assert misc.less_strict_bool(False) is False
    assert misc.less_strict_bool(None) is False


def test_properties():
    class Foo:
        def __init__(self):
            self.var = 1

        @property
        def prop(self):
            return self.var + 1

        def meth(self):
            return self.var + 2

    foo = Foo()
    actual = misc.properties(foo)
    expect = {"var": 1, "prop": 2, "meth": foo.meth}
    assert actual == expect


def test_get_first_duplicate():
    expect = 2
    actual = misc.get_first_duplicate([1, 2, 2, 3])
    assert actual == expect


def test_many_to_one():
    expect = {"a": 1, "b": 1, "c": 2, "d": 2}
    actual = misc.many_to_one({"ab": 1, ("c", "d"): 2})
    assert actual == expect


def test_quote():
    actual = misc.quote(",", ["a", "b"])
    assert actual == "a,b"
    actual = misc.quote([",", ";"], ["a", "b"])
    assert actual == "a,b.a;b"


def test_camel_to_snake():
    actual = misc.camel_to_snake("API_Response")
    assert actual == "api_response"
    actual = misc.camel_to_snake("APIResponse")
    assert actual == "api_response"
    actual = misc.camel_to_snake("APIResponseFactory")
    assert actual == "api_response_factory"


def test_snake_to_camel():
    actual = misc.snake_to_camel("api_response", title_case=True)
    assert actual == "ApiResponse"
    actual = misc.snake_to_camel("api_response_factory", title_case=True)
    assert actual == "ApiResponseFactory"
    actual = misc.snake_to_camel("api_response_factory", title_case=False)
    assert actual == "apiResponseFactory"


def test_use_times_generator():
    auto_id_generator = misc.UseTimesGenerator()
    actual = auto_id_generator("a")
    assert actual == 1
    actual = auto_id_generator("b")
    assert actual == 1
    actual = auto_id_generator("b")
    assert actual == 2
    actual = auto_id_generator("c")
    assert actual == 1


def test_unique_list():
    actual = misc.unique_list(["2", "2", "1"])
    expect = ["2", "1"]
    assert actual == expect

    actual = misc.unique_list(["1", "1", "2"])
    expect = ["1", "2"]
    assert actual == expect

    actual = misc.unique_list([2, 2, 1])
    expect = [2, 1]
    assert actual == expect


def test_strip():
    actual = misc.strip({" a ": [" b ", " c "], " d ": " e ", 1: " f ", 2: 3})
    expect = {1: "f", 2: 3, "a": ["b", "c"], "d": "e"}
    assert actual == expect


def test_get_unique_list():
    actual = misc.get_unique_list(("a", "c", "b", "b", "c", "a"))
    expect = ["a", "c", "b"]
    assert actual == expect
