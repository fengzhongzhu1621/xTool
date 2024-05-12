import pytest

from xTool.compat import flatten_list_bytes, qualname


def test_flatten_list_bytes():
    list_of_data = ["a", "b", "c"]
    with pytest.raises(TypeError):
        flatten_list_bytes(list_of_data)

    list_of_data = [b"a", b"b", b"c"]
    actual = flatten_list_bytes(list_of_data)
    assert actual == b"abc"

    list_of_data = [bytearray("abc", encoding="utf-8"), bytearray("def", encoding="utf-8")]
    actual = flatten_list_bytes(list_of_data)
    assert actual == b"abcdef"


class C:

    def f(self):
        pass

    class D:
        def g(self):
            pass


def f():
    def g():
        pass

    return g


def test_qualname():
    assert qualname(test_flatten_list_bytes) == "test_flatten_list_bytes"

    assert qualname(C) == "C"
    assert qualname(C.f) == "C.f"
    assert qualname(C.D) == "C.D"
    assert qualname(C.D.g) == "C.D.g"

    assert qualname(f) == "f"
    assert qualname(f()) == "f.<locals>.g"
