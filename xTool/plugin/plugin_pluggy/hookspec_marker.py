from typing import Callable, Final, Mapping, TypedDict, final, overload

from xTool.inspect_utils.arg_spec import varnames
from xTool.type_hint import F, Namespace


class HookspecOpts(TypedDict):
    """Options for a hook specification. 存储钩子规范的选项."""

    #: Whether the hook is :ref:`first result only <firstresult>`.
    # 是否仅返回第一个结果
    firstresult: bool
    #: Whether the hook is :ref:`historic <historic>`.
    # 表示这个 hook 是需要保存call history 的，当有新的 plugin 注册的时候，需要回放历史
    historic: bool
    #: Whether the hook :ref:`warns when implemented <warn_on_impl>`.
    # 用于存储一个警告类型（Warning）。当钩子实现注册时，如果设置了此字段，将触发指定的警告。
    # 这有助于提醒开发者关于钩子实现的一些潜在问题。
    warn_on_impl: Warning | None
    #: Whether the hook warns when :ref:`certain arguments are requested
    #: <warn_on_impl>`.
    #:
    #: .. versionadded:: 1.5
    # 用于存储一个字典，其中键是参数名，值是对应的警告类型（Warning）。
    # 当钩子实现请求字典中列出的参数时，将触发相应的警告。这有助于提醒开发者关于钩子实现可能引发的潜在问题。
    warn_on_impl_args: Mapping[str, Warning] | None


# typing.final 仅在类型检查时发挥作用。要确保函数或方法在运行时不可被子类覆盖，
# 你需要使用 Python 的内置 @staticmethod 或 @classmethod 装饰器（对于类方法），
# 并在方法内部添加逻辑来阻止覆盖。


@final
class HookspecMarker:
    """一个用于标记函数作为钩子规范的装饰器，可以理解为定义了一个接口。

    用于定义一个钩子规范（hook specification），它指定了插件可以提供哪些钩子实现。
    HookspecMarker 通常与 pluggy.Hookspec 一起使用，后者定义了一个包含多个钩子规范的类。"""了一个包含多个钩子规范的类。"""

    __slots__ = ("project_name",)

    def __init__(self, project_name: str) -> None:
        # 指定项目名称，当使用相同的 project_name 创建 PluginManager 时，它将自动发现所有标记的函数。
        self.project_name: Final = project_name

    @overload
    def __call__(
        self,
        function: F,  # 用于装饰器函数 F
        firstresult: bool = False,
        historic: bool = False,
        warn_on_impl: Warning | None = None,
        warn_on_impl_args: Mapping[str, Warning] | None = None,
    ) -> F: ...

    @overload  # noqa: F811
    def __call__(  # noqa: F811
        self,
        function: None = ...,
        firstresult: bool = ...,
        historic: bool = ...,
        warn_on_impl: Warning | None = ...,
        warn_on_impl_args: Mapping[str, Warning] | None = ...,
    ) -> Callable[[F], F]: ...

    def __call__(  # noqa: F811
        self,
        function: F | None = None,
        firstresult: bool = False,
        historic: bool = False,
        warn_on_impl: Warning | None = None,
        warn_on_impl_args: Mapping[str, Warning] | None = None,
    ) -> F | Callable[[F], F]:
        def setattr_hookspec_opts(func: F) -> F:
            if historic and firstresult:
                raise ValueError("cannot have a historic firstresult hook")
            opts: HookspecOpts = {
                "firstresult": firstresult,  # 是否仅返回第一个结果
                "historic": historic,  # 是否具有历史记录
                "warn_on_impl": warn_on_impl,
                "warn_on_impl_args": warn_on_impl_args,
            }
            # 给装饰后的函数添加额外属性（存储钩子规范的选项）
            setattr(func, self.project_name + "_spec", opts)
            return func

        if function is not None:
            # 使用 hookspec 装饰器将 function 函数标记为一个钩子规范。这意味着其他插件可以实现这个钩子，从而扩展或修改 function 的行为。
            return setattr_hookspec_opts(function)
        else:
            return setattr_hookspec_opts


@final
class HookSpec:
    __slots__ = (
        "namespace",
        "function",
        "name",
        "argnames",
        "kwargnames",
        "opts",
        "warn_on_impl",
        "warn_on_impl_args",
    )

    def __init__(self, namespace: Namespace, name: str, opts: HookspecOpts) -> None:
        """是一个使用 @final 装饰器标记的类，表示一个钩子规范（hook specification）."""
        # 表示钩子规范所属的命名空间，可以是一个模块（ModuleType）或一个类（type）。
        self.namespace = namespace
        # 表示钩子规范对应的函数或方法。这是通过从命名空间中获取具有相同名称的对象来确定的。
        self.function: Callable[..., object] = getattr(namespace, name)
        # 表示钩子规范的名称，即函数或方法的名称。
        self.name = name
        # 表示钩子规范的位置参数名称 和 关键字参数名称。
        self.argnames, self.kwargnames = varnames(self.function)
        # 表示钩子规范的选项，存储在 HookspecOpts 类型的字典中。
        self.opts = opts
        # 表示当钩子实现注册时应触发的警告。这是从 opts 字典中获取的。
        self.warn_on_impl = opts.get("warn_on_impl")
        # 表示当钩子实现请求特定参数时应触发的警告。这也是从 opts 字典中获取的。
        self.warn_on_impl_args = opts.get("warn_on_impl_args")
