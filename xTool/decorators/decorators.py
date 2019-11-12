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

from xTool.exceptions import AirflowException


def apply_defaults(func):
    """增加对参数的验证逻辑，如果在对象初始化时，参数不全会抛出异常
    Function decorator that Looks for an argument named "default_args", and
    fills the unspecified arguments from it.

    Since python2.* isn't clear about which arguments are missing when
    calling a function, and that this can be quite confusing with multi-level
    inheritance and argument defaults, this decorator also alerts with
    specific information about the missing arguments.
    """
    # 获得函数签名
    import airflow.models
    # Cache inspect.signature for the wrapper closure to avoid calling it
    # at every decorated invocation. This is separate sig_cache created
    # per decoration, i.e. each function decorated using apply_defaults will
    # have a different sig_cache.
    sig_cache = signature(func)


    # 获得默认值为空的参数名，且此参数不为self, 且此参数不为可变参数
    non_optional_args = {
        name for (name, param) in sig_cache.parameters.items()
        if param.default == param.empty and
        param.name != 'self' and
        param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 列表参数最多一个
        if len(args) > 1:
            raise XToolException(
                "Use keyword arguments when initializing operators")
        # 获得参数中的dag对象，或从全局变量中获取dag
        dag_args = {}
        dag_params = {}
        dag = kwargs.get('dag', None) or airflow.models._CONTEXT_MANAGER_DAG
        if dag:
            dag_args = copy(dag.default_args) or {}
            dag_params = copy(dag.params) or {}

        # 把函数的params参数，与dag.parms合并
        params = {}
        if 'params' in kwargs:
            params = kwargs['params']
        dag_params.update(params)

        # 把函数参数中的kwargs['default_args']['params'] 与 dag.parms合并
        # 删除函数参数中的 kwargs['default_args']['params']
        default_args = {}
        if 'default_args' in kwargs:
            default_args = kwargs['default_args']
            if 'params' in default_args:
                dag_params.update(default_args['params'])
                del default_args['params']

        # 把函数参数中kwargs['default_args']，与dag.default_args合并
        dag_args.update(default_args)
        default_args = dag_args


        # 将kwargs['default_args']中的参数合并到函数的kwargs中
        for arg in sig_cache.parameters:
            if arg not in kwargs and arg in default_args:
                kwargs[arg] = default_args[arg]

        # 获得没有设置默认值的参数，抛出异常
        missing_args = list(non_optional_args - set(kwargs))
        if missing_args:
            msg = "Argument {0} is required".format(missing_args)
            raise XToolException(msg)

        kwargs['params'] = dag_params

        result = func(*args, **kwargs)
        return result

    return wrapper


if 'BUILDING_AIRFLOW_DOCS' in os.environ:
    # flake8: noqa: F811
    # Monkey patch hook to get good function headers while building docs
    apply_defaults = lambda x: x
