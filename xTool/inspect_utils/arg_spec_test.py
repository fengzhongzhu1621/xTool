import unittest
from functools import wraps
from typing import cast

from xTool.inspect_utils.arg_spec import format_def, get_full_arg_spec, varnames
from xTool.testing import test_components as tc
from xTool.type_hint import F


# pylint: disable=keyword-arg-before-vararg
def identity3(arg1, arg2: int, arg3=10, arg4: int = 20, *arg5, arg6, arg7: int, arg8=30, arg9: int = 40, **arg10):
    return arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10


class TestGetFullArgSpec(unittest.TestCase):
    def test_get_full_arg_spec(self):
        spec = get_full_arg_spec(tc.identity)
        assert spec.args == ['arg1', 'arg2', 'arg3', 'arg4']
        assert spec.defaults == (10, 20)
        assert spec.varargs == 'arg5'
        assert spec.varkw == 'arg6'
        assert spec.kwonlyargs == []
        assert spec.kwonlydefaults == {}
        assert spec.annotations == {'arg2': int, 'arg4': int}

    def test_get_full_arg_spec_py3(self):
        spec = get_full_arg_spec(identity3)
        assert spec.args == ['arg1', 'arg2', 'arg3', 'arg4']
        assert spec.defaults == (10, 20)
        assert spec.varargs == 'arg5'
        assert spec.varkw == 'arg10'
        assert spec.kwonlyargs == ['arg6', 'arg7', 'arg8', 'arg9']
        assert spec.kwonlydefaults == {'arg8': 30, 'arg9': 40}
        assert spec.annotations == {'arg2': int, 'arg4': int, 'arg7': int, 'arg9': int}

    def test_get_full_arg_spec_from_builtin(self):
        spec = get_full_arg_spec('test'.upper)
        assert spec.args == []
        assert spec.defaults == ()
        assert spec.kwonlyargs == []
        assert spec.kwonlydefaults == {}
        assert spec.annotations == {}

    def test_get_full_arg_spec_from_slot_wrapper(self):
        spec = get_full_arg_spec(tc.NoDefaults)
        self.assertEqual(spec.args, [])
        self.assertEqual(spec.defaults, ())
        self.assertEqual(spec.varargs, None)
        self.assertEqual(spec.varkw, None)
        self.assertEqual(spec.kwonlyargs, [])
        self.assertEqual(spec.kwonlydefaults, {})
        self.assertEqual(spec.annotations, {})

    def testGetFullArgSpecFromNamedTuple(self):
        spec = get_full_arg_spec(tc.NamedTuplePoint)
        self.assertEqual(spec.args, ['x', 'y'])
        self.assertEqual(spec.defaults, ())
        self.assertEqual(spec.varargs, None)
        self.assertEqual(spec.varkw, None)
        self.assertEqual(spec.kwonlyargs, [])
        self.assertEqual(spec.kwonlydefaults, {})
        self.assertEqual(spec.annotations, {})

    def testGetFullArgSpecFromNamedTupleSubclass(self):
        spec = get_full_arg_spec(tc.SubPoint)
        self.assertEqual(spec.args, ['x', 'y'])
        self.assertEqual(spec.defaults, ())
        self.assertEqual(spec.varargs, None)
        self.assertEqual(spec.varkw, None)
        self.assertEqual(spec.kwonlyargs, [])
        self.assertEqual(spec.kwonlydefaults, {})
        self.assertEqual(spec.annotations, {})

    def testGetFullArgSpecFromClassNoInit(self):
        spec = get_full_arg_spec(tc.OldStyleEmpty)
        self.assertEqual(spec.args, [])
        self.assertEqual(spec.defaults, ())
        self.assertEqual(spec.varargs, None)
        self.assertEqual(spec.varkw, None)
        self.assertEqual(spec.kwonlyargs, [])
        self.assertEqual(spec.kwonlydefaults, {})
        self.assertEqual(spec.annotations, {})

    def testGetFullArgSpecFromMethod(self):
        spec = get_full_arg_spec(tc.NoDefaults().double)
        self.assertEqual(spec.args, ['count'])
        self.assertEqual(spec.defaults, ())
        self.assertEqual(spec.varargs, None)
        self.assertEqual(spec.varkw, None)
        self.assertEqual(spec.kwonlyargs, [])
        self.assertEqual(spec.kwonlydefaults, {})
        self.assertEqual(spec.annotations, {})


def test_varnames() -> None:
    def f(x) -> None:
        i = 3  # noqa

    class A:
        def f(self, y) -> None:
            pass

    class B:
        def __call__(self, z) -> None:
            pass

    assert varnames(f) == (("x",), ())
    assert varnames(A().f) == (("y",), ())
    assert varnames(B()) == (("z",), ())


def test_varnames_default() -> None:
    def f(x, y=3) -> None:
        pass

    assert varnames(f) == (("x",), ("y",))


def test_varnames_class() -> None:
    class C:
        def __init__(self, x) -> None:
            pass

    class D:
        pass

    class E:
        def __init__(self, x) -> None:
            pass

    class F:
        pass

    assert varnames(C) == (("x",), ())
    assert varnames(D) == ((), ())
    assert varnames(E) == (("x",), ())
    assert varnames(F) == ((), ())


def test_varnames_keyword_only() -> None:
    def f1(x, *, y) -> None:
        pass

    def f2(x, *, y=3) -> None:
        pass

    def f3(x=1, *, y=3) -> None:
        pass

    assert varnames(f1) == (("x",), ())
    assert varnames(f2) == (("x",), ())
    assert varnames(f3) == ((), ("x",))


def test_varnames_decorator() -> None:

    def my_decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return cast(F, wrapper)

    @my_decorator
    def example(a, b=123) -> None:
        pass

    class Example:
        @my_decorator
        def example_method(self, x, y=1) -> None:
            pass

    ex_inst = Example()

    assert varnames(example) == (("a",), ("b",))
    assert varnames(Example.example_method) == (("x",), ("y",))
    assert varnames(ex_inst.example_method) == (("x",), ("y",))


def test_format_def() -> None:
    def function1():
        pass

    assert format_def(function1) == "function1()"

    def function2(arg1):
        pass

    assert format_def(function2) == "function2(arg1)"

    def function3(arg1, arg2="qwe"):
        pass

    assert format_def(function3) == "function3(arg1, arg2='qwe')"

    def function4(arg1, *args, **kwargs):
        pass

    assert format_def(function4) == "function4(arg1, *args, **kwargs)"
