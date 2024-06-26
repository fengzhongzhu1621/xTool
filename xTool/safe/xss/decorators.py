from functools import wraps


# ===============================================================================
# 转义装饰器
# ===============================================================================
def escape_exempt(view_func):
    """
    转义豁免，被此装饰器修饰的action可以不进行中间件escape
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.escape_exempt = True  # 用于中间件判断
    return wraps(view_func)(wrapped_view)


def escape_script(view_func):
    """
    被此装饰器修饰的action会对GET与POST参数进行javascript escape
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.escape_script = True
    return wraps(view_func)(wrapped_view)


def escape_url(view_func):
    """
    被此装饰器修饰的action会对GET与POST参数进行url escape
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.escape_url = True
    return wraps(view_func)(wrapped_view)


def escape_exempt_param(*param_list, **param_list_dict):
    """
    此装饰器用来豁免某个view函数的某个参数
    @param param_list: 参数列表
    @return:
    """

    def _escape_exempt_param(view_func):
        def wrapped_view(*args, **kwargs):
            return view_func(*args, **kwargs)

        if param_list_dict.get("param_list"):
            wrapped_view.escape_exempt_param = param_list_dict["param_list"]
        else:
            wrapped_view.escape_exempt_param = list(param_list)
        return wraps(view_func)(wrapped_view)

    return _escape_exempt_param
