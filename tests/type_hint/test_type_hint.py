# -*- coding: utf-8 -*-

from xTool.type_hint import get_class_object_init_type


def test_get_class_object_init_type():
    class A:
        def __init__(self, a, b: int, c: int = None):
            pass

    object_type = get_class_object_init_type(A(1, 2, 3), "a")
    assert object_type is None

    object_type = get_class_object_init_type(A(1, 2, 3), "b")
    assert object_type is type(1)
    assert object_type("1") == 1

    object_type = get_class_object_init_type(A(1, 2, 3), "c")
    assert object_type is type(1)
    assert object_type("1") == 1
