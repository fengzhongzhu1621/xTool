from xTool.inspect_utils.callback import get_callback_name
from xTool.testing import test_components as tc


def main_func():
    def child_func():
        pass

    return child_func


class MainClass:
    class Meta:
        pass


lambda_func = lambda x: x.upper()  # noqa


def test_get_callback_name():
    # 函数名
    assert get_callback_name(tc.identity) == "xTool.testing.test_components.identity"
    # 类名
    assert get_callback_name(tc.Empty) == "xTool.testing.test_components.Empty"
    # 命名元组
    assert get_callback_name(tc.NamedTuplePoint) == "xTool.testing.test_components.NamedTuplePoint"
    # 类实例
    # assert (
    #     get_callback_name(tc.CALLABLE_WITH_KEYWORD_ARGUMENT)
    #     == '<xTool.testing.test_components.CallableWithKeywordArgument object at 0x111932cb0>'
    # )
    # 枚举
    assert get_callback_name(tc.Color) == "xTool.testing.test_components.Color"
    # 变量
    var = 1
    assert get_callback_name(var) == '1'
    var = "hello"
    assert get_callback_name(var) == "'hello'"
    # 嵌套函数
    assert get_callback_name(main_func()) == 'xTool.inspect_utils.callback_test.main_func.<locals>.child_func'
    # 嵌套类
    assert get_callback_name(MainClass.Meta) == 'xTool.inspect_utils.callback_test.MainClass.Meta'
    # 匿名函数
    assert get_callback_name(lambda_func) == 'xTool.inspect_utils.callback_test.<lambda>'
