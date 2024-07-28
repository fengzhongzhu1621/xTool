import unittest

from xTool.inspect_utils.arg_spec import get_full_arg_spec
from xTool.testing import test_components as tc


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
