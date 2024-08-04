from .hookimpl_marker import HookimplMarker
from .hookspec_marker import HookspecMarker
from .manage import PluginManager

hookspec = HookspecMarker("myproject")  # hook 标签 用于标记hook
hookimpl = HookimplMarker("myproject")  # hook 实现标签 用于标记hook的一个或多个实现


class MySpec:
    """hook 集合"""

    @hookspec
    def myhook(self, arg1, arg2):
        pass

    @hookspec
    def my_hook_func1(self, arg1, arg2):
        pass

    @hookspec
    def my_hook_func2(self, arg1, arg2):
        pass


# 插件类
class Plugin1:
    """hook实现类1"""

    @hookimpl
    def myhook(self, arg1, arg2):
        print("Plugin1.myhook called")
        return arg1 + arg2

    @hookimpl
    def my_hook_func2(self, arg1, arg2):
        print("Plugin1.my_hook_func2 called, args:", arg1, arg2)
        return arg1 + arg2

    def my_hook_func3(self, arg1, arg2):
        print("Plugin1.my_hook_func3 called, args:", arg1, arg2)
        return arg1 + arg2


class Plugin2:
    """hook实现类2"""

    @hookimpl
    def myhook(self, arg1, arg2):
        print("Plugin2.myhook called")
        return arg1 - arg2

    @hookimpl
    def my_hook_func2(self, arg1, arg2):
        print("Plugin2.my_hook_func2, args:", arg1, arg2)
        return arg1 - arg2


def test_hook():
    # 初始化 PluginManager
    pm = PluginManager("myproject")

    # 登记hook集合(hook函数声明)
    pm.add_hookspecs(MySpec)

    # 注册插件(hook函数实现)
    pm.register(Plugin1())
    pm.register(Plugin2())

    # 调用两个插件类中的同名hook函数, 后注册的插件中的函数会先被调用
    results = pm.hook.myhook(arg1=1, arg2=2)
    assert results == [-1, 3]

    # 只有钩子规范，没有钩子实现，则返回 []
    results = pm.hook.my_hook_func1(arg1=10, arg2=3)
    assert results == []

    results = pm.hook.my_hook_func2(arg1=20, arg2=3)
    assert results == [17, 23]
