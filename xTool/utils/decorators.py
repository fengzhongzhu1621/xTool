# -*- coding: utf-8 -*-

import os

# inspect.signature is only available in Python 3. funcsigs.signature is
# a backport.
try:
    import inspect
    signature = inspect.signature
except AttributeError:
    import funcsigs
    signature = funcsigs.signature

from copy import copy
from functools import wraps

from xTool.exceptions import XToolException


def apply_defaults(func):
    """增加对参数的验证逻辑，如果在对象初始化时，参数不全会抛出异常
    Function decorator that Looks for an argument named "default_args", and
    fills the unspecified arguments from it.

    Since python2.* isn't clear about which arguments are missing when
    calling a function, and that this can be quite confusing with multi-level
    inheritance and argument defaults, this decorator also alerts with
    specific information about the missing arguments.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 列表参数最多一个
        if len(args) > 1:
            raise XToolException(
                "Use keyword arguments when initializing object")
        # 获得参数中的model对象
        model_args = {}
        model_params = {}
        if kwargs.get('model', None):
            model = kwargs.get('model', None)
            model_args = copy(model.default_args) or {}
            model_params = copy(model.params) or {}

        # 把函数的params参数，与model.parms合并
        params = {}
        if 'params' in kwargs:
            params = kwargs['params']
        model_params.update(params)

        # 把函数参数中的kwargs['default_args']['params'] 与 model.parms合并
        # 删除函数参数中的 kwargs['default_args']['params']
        default_args = {}
        if 'default_args' in kwargs:
            default_args = kwargs['default_args']
            if 'params' in default_args:
                model_params.update(default_args['params'])
                del default_args['params']

        # 把函数参数中kwargs['default_args']，与model.default_args合并
        model_args.update(default_args)
        default_args = model_args

        # 获得函数签名
        sig = signature(func)

        # 获得默认值为空的参数名，且此参数不为self, 且此参数不为可变参数
        non_optional_args = [
            name for (name, param) in sig.parameters.items()
            if param.default == param.empty and
            param.name != 'self' and
            param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)]

        # 将kwargs['default_args']中的参数合并到函数的kwargs中
        for arg in sig.parameters:
            if arg in default_args and arg not in kwargs:
                kwargs[arg] = default_args[arg]

        # 获得没有设置默认值的参数，抛出异常
        missing_args = list(set(non_optional_args) - set(kwargs))
        if missing_args:
            msg = "Argument {0} is required".format(missing_args)
            raise XToolException(msg)

        kwargs['params'] = model_params

        result = func(*args, **kwargs)
        return result

    return wrapper


if 'BUILDING_XTOOL_DOCS' in os.environ:
    # Monkey patch hook to get good function headers while building docs
    def apply_defaults(x): return x


if __name__ == '__main__':
    class BashOperator(object):
        template_fields = ('bash_command', 'env')
        template_ext = ('.sh', '.bash',)
        ui_color = '#f0ede4'

        @apply_defaults
        def __init__(
                self,
                bash_command,
                xcom_push=False,
                env=None,
                output_encoding='utf-8',
                *args, **kwargs):

            self.bash_command = bash_command
            self.env = env
            self.xcom_push_flag = xcom_push
            self.output_encoding = output_encoding

    BashOperator(bash_command="ls")
