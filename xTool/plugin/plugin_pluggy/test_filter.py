"""
使用 Pluggy 实现拦截器
"""

from .hookimpl_marker import HookimplMarker
from .hookspec_marker import HookspecMarker
from .manage import PluginManager

hookspec = HookspecMarker("xTool.filter")
hookimpl = HookimplMarker("xTool.filter")


class FilterSpec:
    """拦截器接口 ."""

    @hookspec
    def process_request(self, request):
        pass

    @hookspec
    def process_response(self, request, response):
        pass

    @hookspec
    def process_view(self, request, view_func, view_args, view_kwargs):
        pass


class FilterPlugin1:
    @hookimpl
    def process_request(self, request):
        request.data["result"].append("FilterPlugin1")

    @hookimpl(wrapper=True)
    def process_response(self, request, response):
        response.data["data"].append("FilterPlugin1 before yield")
        # 接受插件 FilterPlugin2 的返回结果
        results = yield
        results.append("FilterPlugin1")
        response.data["data"].append("FilterPlugin1 after yield")
        return results


class FilterPlugin2:
    @hookimpl
    def process_request(self, request):
        request.data["result"].append("FilterPlugin2")

    @hookimpl(wrapper=True)
    def process_response(self, request, response):
        response.data["data"].append("FilterPlugin2 before yield")
        # 接受插件 FilterPlugin3 的返回结果
        results = yield
        results.append("FilterPlugin2")
        response.data["data"].append("FilterPlugin2 after yield")
        return results


class FilterPlugin3:
    @hookimpl
    def process_request(self, request):
        request.data["result"].append("FilterPlugin3")

    @hookimpl(wrapper=True)
    def process_response(self, request, response):
        response.data["data"].append("FilterPlugin3 before yield")
        # 接受其他插件的执行结果
        results = yield
        results.append("FilterPlugin3")
        response.data["data"].append("FilterPlugin3 after yield")
        return results


# 初始化 PluginManager
pm = PluginManager("xTool.filter")

# 登记hook集合(hook函数声明)
pm.add_hookspecs(FilterSpec)

# 注册插件(hook函数实现)
pm.register(FilterPlugin3())
pm.register(FilterPlugin2())
pm.register(FilterPlugin1())


class Request:
    def __init__(self):
        self.data = {"result": []}


class Response:
    def __init__(self):
        self.data = {
            "code": 0,
            "data": [],
            "message": "",
        }


def test_hook_request():
    # 调用两个插件类中的同名hook函数, 后注册的插件中的函数会先被调用
    request = Request()
    results = pm.hook.process_request(request=request)
    assert results == []  # 钩子实现返回 None
    assert request.data == {'result': ['FilterPlugin1', 'FilterPlugin2', 'FilterPlugin3']}


def test_hook_response():
    request = Request()
    response = Response()
    results = pm.hook.process_response(request=request, response=response)
    assert results == ['FilterPlugin3', 'FilterPlugin2', 'FilterPlugin1']
    assert response.data == {
        'code': 0,
        'data': [
            'FilterPlugin1 before yield',
            'FilterPlugin2 before yield',
            'FilterPlugin3 before yield',
            'FilterPlugin3 after yield',
            'FilterPlugin2 after yield',
            'FilterPlugin1 after yield',
        ],
        'message': '',
    }
