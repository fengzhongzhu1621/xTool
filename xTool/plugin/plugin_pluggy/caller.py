import warnings
from typing import (
    TYPE_CHECKING,
    AbstractSet,
    Any,
    Callable,
    Final,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    final,
)

from xTool.type_hint import F, Namespace

from .hookimpl_marker import HookImpl, HookimplOpts
from .hookspec_marker import HookSpec, HookspecOpts
from .type_hint import _Plugin

_HookExec = Callable[
    [str, Sequence["HookImpl"], Mapping[str, object], bool],
    Union[object, List[object]],
]
_CallHistory = List[Tuple[Mapping[str, object], Optional[Callable[[Any], None]]]]


class HookCaller:
    """A caller of all registered implementations of a hook specification.
    用于调用已注册的所有实现特定钩子规范的插件。"""

    __slots__ = (
        "name",
        "spec",
        "_hookexec",
        "_hookimpls",
        "_call_history",
    )

    def __init__(
        self,
        name: str,  # 钩子的名称
        hook_execute: _HookExec,  # 用于执行钩子的函数
        specmodule_or_class: Namespace | None = None,  # 可选参数，用于指定钩子规范的模块或类。
        spec_opts: HookspecOpts | None = None,  # 可选参数，用于指定钩子规范的选项。
    ) -> None:
        """:meta private:"""
        #: Name of the hook getting called.
        self.name: Final = name
        self._hookexec: Final = hook_execute
        # The hookimpls list. The caller iterates it *in reverse*. Format:
        # 1. trylast nonwrappers
        # 2. nonwrappers
        # 3. tryfirst nonwrappers
        # 4. trylast wrappers
        # 5. wrappers
        # 6. tryfirst wrappers
        # 回调链，包含了注册的钩子函数的实现
        self._hookimpls: Final[list[HookImpl]] = []
        self._call_history: _CallHistory | None = None
        # # 设置一个钩子规范
        self.spec: HookSpec | None = None
        if specmodule_or_class is not None:
            assert spec_opts is not None
            self.set_specification(specmodule_or_class, spec_opts)

    def set_specification(
        self,
        specmodule_or_class: Namespace,  # 用于指定钩子规范的模块或类
        spec_opts: HookspecOpts,  # 用于指定钩子规范的选项。
    ) -> None:
        """设置一个钩子规范"""
        if self.spec is not None:
            raise ValueError(
                f"Hook {self.spec.name!r} is already registered " f"within namespace {self.spec.namespace}"
            )
        self.spec = HookSpec(specmodule_or_class, self.name, spec_opts)
        if spec_opts.get("historic"):
            self._call_history = []

    def _add_hookimpl(self, hookimpl: HookImpl) -> None:
        """Add an implementation to the callback chain.
        向回调链中添加一个实现。"""
        # 获得回调链的插入点，从包含 wrapper 参数的钩子实现后面开始处理，获得可插入的回调链插槽范围
        for i, method in enumerate(self._hookimpls):
            if method.wrapper:
                splitpoint = i
                break
        else:
            splitpoint = len(self._hookimpls)
        if hookimpl.wrapper:
            start, end = splitpoint, len(self._hookimpls)
        else:
            start, end = 0, splitpoint
        # 在回调链中插入钩子实现
        if hookimpl.trylast:
            self._hookimpls.insert(start, hookimpl)
        elif hookimpl.tryfirst:
            self._hookimpls.insert(end, hookimpl)
        else:
            # find last non-tryfirst method
            # 因为回调链逆序执行，排除掉标记为 tryfirst 标记为优先执行的钩子实现，在其后插入新的钩子实现
            i = end - 1
            while i >= start and self._hookimpls[i].tryfirst:
                i -= 1
            self._hookimpls.insert(i + 1, hookimpl)

    def _remove_plugin(self, plugin: _Plugin) -> None:
        """从回调链中删除指定的插件。"""
        for i, method in enumerate(self._hookimpls):
            if method.plugin == plugin:
                del self._hookimpls[i]
                return
        raise ValueError(f"plugin {plugin!r} not found")

    def get_hookimpls(self) -> List[HookImpl]:
        """Get all registered hook implementations for this hook.
        获取此钩子的所有已注册实现。"""
        return self._hookimpls.copy()

    def _verify_all_args_are_provided(self, kwargs: Mapping[str, object]) -> None:
        """验证 kwargs 中的每个参数名是否在钩子规范函数位置参数中。如果没有提供所有必需的参数，将发出警告。"""
        # This is written to avoid expensive operations when not needed.
        if not self.spec:
            return
        # 遍历钩子规范函数的位置参数
        for argname in self.spec.argnames:
            if argname not in kwargs:
                notincall = ", ".join(
                    repr(argname)
                    for argname in self.spec.argnames
                    # Avoid self.spec.argnames - kwargs.keys() - doesn't preserve order.
                    if argname not in kwargs.keys()
                )
                warnings.warn(
                    "Argument(s) {} which are declared in the hookspec "
                    "cannot be found in this hook call".format(notincall),
                    stacklevel=2,
                )
                break

    def __call__(self, **kwargs: object) -> Any:
        """Call the hook.

        Only accepts keyword arguments, which should match the hook
        specification.

        Returns the result(s) of calling all registered plugins, see
        :ref:`calling`.
        """
        # 确认调用时不需要保存历史
        assert not self.is_historic(), "Cannot directly call a historic hook - use call_historic instead."
        # 验证输入参数是否符合钩子规范
        self._verify_all_args_are_provided(kwargs)
        # 判断是否返回第一个钩子实现的结果
        firstresult = self.spec.opts.get("firstresult", False) if self.spec else False
        # Copy because plugins may register other plugins during iteration (#438).
        # 执行回调链
        return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)

    def call_historic(
        self,
        result_callback: Callable[[Any], None] | None = None,
        kwargs: Mapping[str, object] | None = None,
    ) -> None:
        """Call the hook with given ``kwargs`` for all registered plugins and
        for all plugins which will be registered afterwards, see
        :ref:`historic`.

        :param result_callback:
            If provided, will be called for each non-``None`` result obtained
            from a hook implementation.
        """
        # 确认调用时需要保存历史
        assert self.is_historic()
        kwargs = kwargs or {}
        # 验证输入参数是否符合钩子规范
        self._verify_all_args_are_provided(kwargs)
        # 记录请求参数和结果回调
        self._call_history.append((kwargs, result_callback))
        # Historizing hooks don't return results.
        # Remember firstresult isn't compatible with historic.
        # Copy because plugins may register other plugins during iteration (#438).
        # 执行回调链
        res = self._hookexec(self.name, self._hookimpls.copy(), kwargs, False)
        if result_callback is None:
            return
        # 执行回调
        if isinstance(res, list):
            for x in res:
                result_callback(x)

    def _maybe_apply_history(self, method: HookImpl) -> None:
        """Apply call history to a new hookimpl if it is marked as historic.
        使用指定的钩子实现，执行历史上已经执行过的参数和回调"""
        if not self.is_historic():
            return
        assert self._call_history is not None
        # 遍历执行历史
        for kwargs, result_callback in self._call_history:
            # 执行指定的钩子实现
            res = self._hookexec(self.name, [method], kwargs, False)
            if res and result_callback is not None:
                # XXX: remember firstresult isn't compat with historic
                assert isinstance(res, list)
                result_callback(res[0])

    def call_extra(self, methods: Sequence[F], kwargs: Mapping[str, object]) -> Any:
        """Call the hook with some additional temporarily participating
        methods using the specified ``kwargs`` as call parameters, see
        :ref:`call_extra`.
        使用指定的 kwargs 作为调用参数，调用钩子并添加一些额外的临时参与方法。"""
        # 确认调用时不需要保存历史
        assert not self.is_historic(), "Cannot directly call a historic hook - use call_historic instead."
        # 验证输入参数是否符合钩子规范
        self._verify_all_args_are_provided(kwargs)
        opts: HookimplOpts = {
            "wrapper": False,
            "optionalhook": False,
            "trylast": False,
            "tryfirst": False,
            "specname": None,
        }
        hookimpls = self._hookimpls.copy()
        for method in methods:
            # 创建一个临时的钩子实现
            hookimpl = HookImpl(None, "<temp>", method, opts)
            # 将临时的钩子实现插入到回调链中
            # Find last non-tryfirst nonwrapper method.
            i = len(hookimpls) - 1
            while i >= 0 and (
                # Skip wrappers.
                hookimpls[i].wrapper
                # Skip tryfirst nonwrappers.
                or hookimpls[i].tryfirst
            ):
                i -= 1
            hookimpls.insert(i + 1, hookimpl)
        # 执行回调链
        firstresult = self.spec.opts.get("firstresult", False) if self.spec else False
        return self._hookexec(self.name, hookimpls, kwargs, firstresult)

    def has_spec(self) -> bool:
        """返回一个布尔值，表示此 HookCaller 是否具有钩子规范。"""
        return self.spec is not None

    def is_historic(self) -> bool:
        """Whether this caller is :ref:`historic <historic>`.
        返回一个布尔值，表示此调用者是否是历史性的（即是否记录了调用历史）。"""
        return self._call_history is not None

    def __repr__(self) -> str:
        return f"<HookCaller {self.name!r}>"


class SubsetHookCaller(HookCaller):
    """A proxy to another HookCaller which manages calls to all registered
    plugins except the ones from remove_plugins.
    充当另一个 HookCaller 的代理，管理对所有已注册插件的调用，但排除 remove_plugins 中的插件。"""

    __slots__ = (
        "_orig",
        "_remove_plugins",
    )

    def __init__(self, orig: HookCaller, remove_plugins: AbstractSet[_Plugin]) -> None:
        self._orig = orig
        self._remove_plugins = remove_plugins
        self.name = orig.name  # type: ignore[misc]
        self._hookexec = orig._hookexec  # type: ignore[misc]

    @property  # type: ignore[misc]
    def _hookimpls(self) -> list[HookImpl]:
        """返回一个列表，其中包含原始 HookCaller 实例中的所有实现，但不包括 remove_plugins 中的插件。"""
        return [impl for impl in self._orig._hookimpls if impl.plugin not in self._remove_plugins]

    @property
    def spec(self) -> HookSpec | None:  # type: ignore[override]
        """返回原始 HookCaller 实例的钩子规范。"""
        return self._orig.spec

    @property
    def _call_history(self) -> _CallHistory | None:  # type: ignore[override]
        """返回原始 HookCaller 实例的调用历史。"""
        return self._orig._call_history

    def __repr__(self) -> str:
        return f"<_SubsetHookCaller {self.name!r}>"


@final
class HookRelay:
    """Hook holder object for performing 1:N hook calls where N is the number
    of registered plugins.
    用于执行 1:N 的钩子调用，其中 N 是已注册插件的数量。HookRelay 类充当钩子的持有者对象，用于管理钩子的调用。
    """

    __slots__ = ("__dict__",)

    def __init__(self) -> None:
        """:meta private:"""

    if TYPE_CHECKING:
        # 当访问一个不存在的属性时，这个方法会被调用。在这个例子中，__getattr__ 方法返回一个 HookCaller 类型的对象。
        # 这个方法仅在类型检查时存在，用于提供更好的类型提示。
        def __getattr__(self, name: str) -> HookCaller: ...
