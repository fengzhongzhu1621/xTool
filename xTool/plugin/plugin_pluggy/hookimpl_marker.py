from typing import Callable, Final, TypedDict, final, overload

from xTool.inspect_utils.arg_spec import varnames
from xTool.type_hint import F

from .result import _HookImplFunction
from .type_hint import _Plugin


class HookimplOpts(TypedDict):
    """Options for a hook implementation. 用于存储钩子实现（hook implementation）的选项，可以理解为是接口的实现 ."""

    #: Whether the hook implementation is a :ref:`wrapper <hookwrapper>`.
    # 一个布尔值，表示钩子实现是否是一个包装器（wrapper）。包装器是一种特殊类型的钩子实现，可以在不修改原始实现的情况下添加额外的行为。
    wrapper: bool
    #: Whether validation against a hook specification is :ref:`optional
    #: <optionalhook>`.
    # 一个布尔值，表示是否应跳过针对钩子规范的验证。如果设置为 True，则钩子实现不会受到钩子规范的约束，可以具有任意签名。
    optionalhook: bool
    #: Whether to try to order this hook implementation :ref:`first
    #: <callorder>`.
    # 一个布尔值，表示是否尝试将此钩子实现排在调用顺序的第一位。这有助于确保某些重要的钩子实现优先于其他实现执行。
    tryfirst: bool
    #: Whether to try to order this hook implementation :ref:`last
    #: <callorder>`.
    # 一个布尔值，表示是否尝试将此钩子实现排在调用顺序的最后一位。这有助于确保某些钩子实现在其他实现之后执行。
    trylast: bool
    #: The name of the hook specification to match, see :ref:`specname`.
    # 一个字符串或 None，表示要匹配的钩子规范的名称。如果设置了此选项，钩子实现将仅与具有相同名称的钩子规范匹配。
    # 这对于在多个规范中共享相同的钩子实现非常有用。
    specname: str | None


@final
class HookimplMarker:
    """Decorator for marking functions as hook implementations.

    Instantiate it with a ``project_name`` to get a decorator.
    Calling :meth:`PluginManager.register` later will discover all marked
    functions if the :class:`PluginManager` uses the same project name.
    """

    __slots__ = ("project_name",)

    def __init__(self, project_name: str) -> None:
        self.project_name: Final = project_name

    @overload
    def __call__(
        self,
        function: F,
        optionalhook: bool = ...,
        tryfirst: bool = ...,
        trylast: bool = ...,
        specname: str | None = ...,
        wrapper: bool = ...,
    ) -> F: ...

    @overload  # noqa: F811
    def __call__(  # noqa: F811 E704
        self,
        function: None = ...,
        optionalhook: bool = ...,
        tryfirst: bool = ...,
        trylast: bool = ...,
        specname: str | None = ...,
        wrapper: bool = ...,
    ) -> Callable[[F], F]: ...

    def __call__(  # noqa: F811
        self,
        function: F | None = None,
        optionalhook: bool = False,
        tryfirst: bool = False,
        trylast: bool = False,
        specname: str | None = None,
        wrapper: bool = False,
    ) -> F | Callable[[F], F]:
        """If passed a function, directly sets attributes on the function
        which will make it discoverable to :meth:`PluginManager.register`.

        If passed no function, returns a decorator which can be applied to a
        function later using the attributes supplied.
        """

        def setattr_hookimpl_opts(func: F) -> F:
            opts: HookimplOpts = {
                "wrapper": wrapper,
                "optionalhook": optionalhook,
                "tryfirst": tryfirst,
                "trylast": trylast,
                "specname": specname,
            }
            setattr(func, self.project_name + "_impl", opts)
            return func

        if function is None:
            return setattr_hookimpl_opts
        else:
            return setattr_hookimpl_opts(function)


def normalize_hookimpl_opts(opts: HookimplOpts) -> None:
    opts.setdefault("tryfirst", False)
    opts.setdefault("trylast", False)
    opts.setdefault("wrapper", False)
    opts.setdefault("optionalhook", False)
    opts.setdefault("specname", None)


@final
class HookImpl:
    """A hook implementation in a :class:`HookCaller`. 使用 @final 装饰器标记的类，表示一个钩子实现（hook implementation）."""

    __slots__ = (
        "function",
        "argnames",
        "kwargnames",
        "plugin",
        "opts",
        "plugin_name",
        "wrapper",
        "optionalhook",
        "tryfirst",
        "trylast",
    )

    def __init__(
        self,
        plugin: _Plugin,
        plugin_name: str,  # 默认是 plugin 插件实例的 id(plugin) 值
        function: _HookImplFunction,  # 通常是 plugin 类中的使用了 @hookimpl 的方法
        hook_impl_opts: HookimplOpts,  # @hookimpl 装饰的方法的 _impl 属性值
    ) -> None:
        """接受一个插件对象（_Plugin 类型）、插件名称（str 类型）、
        一个钩子实现函数（_HookImplFunction 类型）和一个钩子实现选项对象（HookimplOpts 类型）。
        它初始化类的属性，并提取钩子实现的参数名称和选项。"""
        #: The hook implementation function.
        # 表示钩子实现的函数或方法。
        self.function: Final = function
        # 表示钩子实现的位置参数名称 和 关键字参数名称。
        argnames, kwargnames = varnames(self.function)
        #: The positional parameter names of ``function```.
        self.argnames: Final = argnames
        #: The keyword parameter names of ``function```.
        self.kwargnames: Final = kwargnames
        #: The plugin which defined this hook implementation.
        # 表示定义此钩子实现的插件对象。
        self.plugin: Final = plugin
        # 表示配置此钩子实现的选项，存储在 HookimplOpts 类型的字典中。
        #: The :class:`HookimplOpts` used to configure this hook implementation.
        self.opts: Final = hook_impl_opts
        #: The name of the plugin which defined this hook implementation.
        # 表示定义此钩子实现的插件的名称。
        self.plugin_name: Final = plugin_name
        #: Whether the hook implementation is a :ref:`wrapper <hookwrapper>`.
        # 一个布尔值，表示钩子实现是否是一个包装器（wrapper）。
        self.wrapper: Final = hook_impl_opts["wrapper"]
        #: Whether validation against a hook specification is :ref:`optional
        #: <optionalhook>`.
        # 一个布尔值，表示是否应跳过针对钩子规范的验证。
        self.optionalhook: Final = hook_impl_opts["optionalhook"]
        #: Whether to try to order this hook implementation :ref:`first
        #: <callorder>`.
        # 一个布尔值，表示是否尝试将此钩子实现排在调用顺序的第一位。
        self.tryfirst: Final = hook_impl_opts["tryfirst"]
        #: Whether to try to order this hook implementation :ref:`last
        #: <callorder>`.
        # 一个布尔值，表示是否尝试将此钩子实现排在调用顺序的最后一位。
        self.trylast: Final = hook_impl_opts["trylast"]

    def __repr__(self) -> str:
        return f"<HookImpl plugin_name={self.plugin_name!r}, plugin={self.plugin!r}>"
