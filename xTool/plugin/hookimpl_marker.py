from typing import Callable, Final, TypedDict, final, overload

from xTool.type_hint import F


class HookimplOpts(TypedDict):
    """Options for a hook implementation. 用于存储钩子实现（hook implementation）的选项 ."""

    #: Whether the hook implementation is a :ref:`wrapper <hookwrapper>`.
    # 一个布尔值，表示钩子实现是否是一个包装器（wrapper）。包装器是一种特殊类型的钩子实现，可以在不修改原始实现的情况下添加额外的行为。
    wrapper: bool
    #: Whether the hook implementation is an :ref:`old-style wrapper
    #: <old_style_hookwrappers>`.
    # 一个布尔值，表示钩子实现是否是一个旧式包装器（old-style wrapper）。
    # 旧式包装器在 pluggy 的较旧版本中使用，现在已经被新的包装器机制取代。通常，你不需要设置此选项。
    hookwrapper: bool
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
        hookwrapper: bool = ...,
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
        hookwrapper: bool = ...,
        optionalhook: bool = ...,
        tryfirst: bool = ...,
        trylast: bool = ...,
        specname: str | None = ...,
        wrapper: bool = ...,
    ) -> Callable[[F], F]: ...

    def __call__(  # noqa: F811
        self,
        function: F | None = None,
        hookwrapper: bool = False,
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
                "hookwrapper": hookwrapper,
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
