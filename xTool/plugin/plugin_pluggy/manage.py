import inspect
from typing import TYPE_CHECKING, Any, Callable, Final, Iterable, Mapping, Sequence

from xTool.inspect_utils.arg_spec import format_def
from xTool.type_hint import F, Namespace

from .call import multicall
from .caller import HookCaller, HookRelay, SubsetHookCaller
from .exceptions import PluginValidationError
from .hookimpl_marker import HookImpl, HookimplOpts, normalize_hookimpl_opts
from .hookspec_marker import HookspecOpts
from .pkg import DistFacade
from .result import Result
from .tracing import TagTracer, TagTracerSub
from .type_hint import _Plugin
from .warnings import warn_for_function

if TYPE_CHECKING:
    # importtlib.metadata import is slow, defer it.
    import importlib.metadata


_BeforeTrace = Callable[[str, Sequence[HookImpl], Mapping[str, Any]], None]
_AfterTrace = Callable[[Result[Any], str, Sequence[HookImpl], Mapping[str, Any]], None]


class PluginManager:
    def __init__(self, project_name: str) -> None:
        #: The project name.
        # 项目名称
        self.project_name: Final = project_name
        # 插件字典
        self._name2plugin: Final[dict[str, _Plugin]] = {}
        # 插件分布信息列表
        self._plugin_distinfo: Final[list[tuple[_Plugin, DistFacade]]] = []
        #: The "hook relay", used to call a hook on all registered plugins.
        #: See :ref:`calling`.
        # 钩子中继，钩子的规范名和 HookCaller 的映射关系
        self.hook: Final = HookRelay()
        #: The tracing entry point. See :ref:`tracing`.
        # 跟踪入口点
        self.trace: Final[TagTracerSub] = TagTracer().get("pluginmanage")
        # 内部钩子执行方法
        self._inner_hookexec = multicall

    def register(self, plugin: _Plugin, name: str | None = None) -> str | None:
        """Register a plugin and return its name.

        :param name:
            The name under which to register the plugin. If not specified, a
            name is generated using :func:`get_canonical_name`.

        :returns:
            The plugin name. If the name is blocked from registering, returns
            ``None``.

        If the plugin is already registered, raises a :exc:`ValueError`.
        """
        # 返回一个插件对象的规范名称
        plugin_name = name or self.get_canonical_name(plugin)

        # 判断插件是否已经注册
        if plugin_name in self._name2plugin:
            if self._name2plugin.get(plugin_name, -1) is None:
                return None  # blocked plugin, return None to indicate no registration
            raise ValueError("Plugin name already registered: {}={}\n{}".format(plugin_name, plugin, self._name2plugin))
        if plugin in self._name2plugin.values():
            raise ValueError(
                "Plugin already registered under a different name: {}={}\n{}".format(
                    plugin_name, plugin, self._name2plugin
                )
            )

        # 添加插件
        # XXX if an error happens we should make sure no state has been
        # changed at point of return
        self._name2plugin[plugin_name] = plugin

        # register matching hook implementations of the plugin
        # 获得插件类实例的所有方法
        tmp = dir(plugin)
        for name in tmp:
            if name.startswith("__"):
                continue
            # 获得插件中 @hookimpl 装饰的方法的 _impl 属性，即方法配置的 HookimplOpts 对象的值
            hookimpl_opts = self.parse_hookimpl_opts(plugin, name)
            if hookimpl_opts is not None:
                # 设置默认属性
                normalize_hookimpl_opts(hookimpl_opts)
                # 获得插件方法
                method: F[object] = getattr(plugin, name)
                # 将插件方法转换为 HookImpl 对象
                hookimpl = HookImpl(plugin, plugin_name, method, hookimpl_opts)
                # 获得钩子的规范名
                name = hookimpl_opts.get("specname") or name
                # 根据钩子的规范名获取一个 HookCaller 对象
                hook: HookCaller | None = getattr(self.hook, name, None)
                if hook is None:
                    # 为每个钩子设置一个调用者
                    hook = HookCaller(name, self._hookexec)
                    setattr(self.hook, name, hook)

                if hook.has_spec():
                    self._verify_hook(hook, hookimpl)
                    hook._maybe_apply_history(hookimpl)

                # 将钩子实现添加到钩子执行器中
                hook._add_hookimpl(hookimpl)

        return plugin_name

    def unregister(self, plugin: _Plugin | None = None, name: str | None = None) -> Any | None:
        """Unregister a plugin and all of its hook implementations.

        The plugin can be specified either by the plugin object or the plugin
        name. If both are specified, they must agree.

        Returns the unregistered plugin, or ``None`` if not found.
        """
        if name is None:
            assert plugin is not None, "one of name or plugin needs to be specified"
            name = self.get_name(plugin)
            assert name is not None, "plugin is not registered"

        if plugin is None:
            plugin = self.get_plugin(name)
            if plugin is None:
                return None

        hookcallers = self.get_hookcallers(plugin)
        if hookcallers:
            for hookcaller in hookcallers:
                hookcaller._remove_plugin(plugin)

        # if self._name2plugin[name] == None registration was blocked: ignore
        if self._name2plugin.get(name):
            assert name is not None
            del self._name2plugin[name]

        return plugin

    def get_canonical_name(self, plugin: _Plugin) -> str:
        """Return a canonical name for a plugin object.
        用于返回一个插件对象的规范名称。规范名称是指插件的原始名称，不考虑它在注册时可能被指定的其他名称。

        Note that a plugin may be registered under a different name
        specified by the caller of :meth:`register(plugin, name) <register>`.
        To obtain the name of a registered plugin use :meth:`get_name(plugin)
        <get_name>` instead.
        """
        name: str | None = getattr(plugin, "__name__", None)
        return name or str(id(plugin))

    def parse_hookimpl_opts(self, plugin: _Plugin, name: str) -> HookimplOpts | None:
        """Try to obtain a hook implementation from an item with the given name
        in the given plugin which is being searched for hook impls.
        获得插件中 @hookimpl 装饰的方法的 _impl 属性，即方法配置的 HookimplOpts 对象的值

        :returns:
            The parsed hookimpl options, or None to skip the given item.

        This method can be overridden by ``PluginManager`` subclasses to
        customize how hook implementation are picked up. By default, returns the
        options for items decorated with :class:`HookimplMarker`.
        """
        method: object = getattr(plugin, name)
        # 检查一个对象是否是一个常规的函数或方法。这个函数可以用来确定一个对象是否可以被调用，就像函数或方法一样。
        if not inspect.isroutine(method):
            return None
        # 获得插件中 @hookimpl 装饰的方法的 _impl 属性值
        try:
            res: HookimplOpts | None = getattr(method, self.project_name + "_impl", None)
        except Exception:
            res = {}  # type: ignore[assignment]
        if res is not None and not isinstance(res, dict):
            # false positive
            res = None  # type:ignore[unreachable]
        return res

    def get_name(self, plugin: _Plugin) -> str | None:
        """Return the name the plugin is registered under, or ``None`` if
        is isn't."""
        for name, val in self._name2plugin.items():
            if plugin == val:
                return name
        return None

    def get_plugin(self, name: str) -> Any | None:
        """Return the plugin registered under the given name, if any."""
        return self._name2plugin.get(name)

    def has_plugin(self, name: str) -> bool:
        """Return whether a plugin with the given name is registered."""
        return self.get_plugin(name) is not None

    def get_plugins(self) -> set[Any]:
        """Return a set of all registered plugin objects."""
        return {x for x in self._name2plugin.values() if x is not None}

    def is_registered(self, plugin: _Plugin) -> bool:
        """Return whether the plugin is already registered."""
        return any(plugin == val for val in self._name2plugin.values())

    def list_plugin_distinfo(self) -> list[tuple[_Plugin, DistFacade]]:
        """Return a list of (plugin, distinfo) pairs for all
        setuptools-registered plugins."""
        return list(self._plugin_distinfo)

    def list_name_plugin(self) -> list[tuple[str, _Plugin]]:
        """Return a list of (name, plugin) pairs for all registered plugins."""
        return list(self._name2plugin.items())

    def set_blocked(self, name: str) -> None:
        """Block registrations of the given name, unregister if already registered."""
        self.unregister(name=name)
        self._name2plugin[name] = None

    def is_blocked(self, name: str) -> bool:
        """Return whether the given plugin name is blocked."""
        return name in self._name2plugin and self._name2plugin[name] is None

    def unblock(self, name: str) -> bool:
        """Unblocks a name.

        Returns whether the name was actually blocked.
        """
        if self._name2plugin.get(name, -1) is None:
            del self._name2plugin[name]
            return True
        return False

    def get_hookcallers(self, plugin: _Plugin) -> list[HookCaller] | None:
        """Get all hook callers for the specified plugin.

        :returns:
            The hook callers, or ``None`` if ``plugin`` is not registered in
            this plugin manager.
        """
        if self.get_name(plugin) is None:
            return None
        hookcallers = []
        for hookcaller in self.hook.__dict__.values():
            for hookimpl in hookcaller.get_hookimpls():
                if hookimpl.plugin is plugin:
                    hookcallers.append(hookcaller)
        return hookcallers

    def _hookexec(
        self,
        hook_name: str,
        methods: Sequence[HookImpl],
        kwargs: Mapping[str, object],
        firstresult: bool,
    ) -> object | list[object]:
        # called from all hookcaller instances.
        # enable_tracing will set its own wrapping function at self._inner_hookexec
        return self._inner_hookexec(hook_name, methods, kwargs, firstresult)

    def add_hookspecs(self, module_or_class: Namespace) -> None:
        """Add new hook specifications defined in the given ``module_or_class``.

        Functions are recognized as hook specifications if they have been
        decorated with a matching :class:`HookspecMarker`.
        """
        names = []
        for name in dir(module_or_class):
            if name.startswith("__"):
                continue
            # 获得插件中 @hookspec 装饰的方法的 _spec 属性，即方法配置的 HookspecOpts 对象的值
            spec_opts = self.parse_hookspec_opts(module_or_class, name)
            if spec_opts is not None:
                hc: HookCaller | None = getattr(self.hook, name, None)
                if hc is None:
                    hc = HookCaller(name, self._hookexec, module_or_class, spec_opts)
                    setattr(self.hook, name, hc)
                else:
                    # Plugins registered this hook without knowing the spec.
                    # 给钩子执行器设置一个钩子规范
                    hc.set_specification(module_or_class, spec_opts)
                    for hookfunction in hc.get_hookimpls():
                        self._verify_hook(hc, hookfunction)
                names.append(name)

        if not names:
            raise ValueError(f"did not find any {self.project_name!r} hooks in {module_or_class!r}")

    def parse_hookspec_opts(self, module_or_class: Namespace, name: str) -> HookspecOpts | None:
        """Try to obtain a hook specification from an item with the given name
        in the given module or class which is being searched for hook specs.

        :returns:
            The parsed hookspec options for defining a hook, or None to skip the
            given item.

        This method can be overridden by ``PluginManager`` subclasses to
        customize how hook specifications are picked up. By default, returns the
        options for items decorated with :class:`HookspecMarker`.
        """
        method = getattr(module_or_class, name)
        opts: HookspecOpts | None = getattr(method, self.project_name + "_spec", None)
        return opts

    def _verify_hook(self, hook: HookCaller, hookimpl: HookImpl) -> None:
        if hook.is_historic() and hookimpl.wrapper:
            raise PluginValidationError(
                hookimpl.plugin,
                "Plugin %r\nhook %r\nhistoric incompatible with yield/wrapper/hookwrapper"
                % (hookimpl.plugin_name, hook.name),
            )

        assert hook.spec is not None
        if hook.spec.warn_on_impl:
            warn_for_function(hook.spec.warn_on_impl, hookimpl.function)

        # positional arg checking
        notinspec = set(hookimpl.argnames) - set(hook.spec.argnames)
        if notinspec:
            raise PluginValidationError(
                hookimpl.plugin,
                "Plugin %r for hook %r\nhookimpl definition: %s\n"
                "Argument(s) %s are declared in the hookimpl but "
                "can not be found in the hookspec"
                % (
                    hookimpl.plugin_name,
                    hook.name,
                    format_def(hookimpl.function),
                    notinspec,
                ),
            )

        if hook.spec.warn_on_impl_args:
            for hookimpl_argname in hookimpl.argnames:
                argname_warning = hook.spec.warn_on_impl_args.get(hookimpl_argname)
                if argname_warning is not None:
                    warn_for_function(argname_warning, hookimpl.function)

        if hookimpl.wrapper and not inspect.isgeneratorfunction(hookimpl.function):
            raise PluginValidationError(
                hookimpl.plugin,
                "Plugin %r for hook %r\nhookimpl definition: %s\n"
                "Declared as wrapper=True or hookwrapper=True "
                "but function is not a generator function"
                % (hookimpl.plugin_name, hook.name, format_def(hookimpl.function)),
            )

    def check_pending(self) -> None:
        """Verify that all hooks which have not been verified against a
        hook specification are optional, otherwise raise
        :exc:`PluginValidationError`."""
        for name in self.hook.__dict__:
            if name[0] != "_":
                hook: HookCaller = getattr(self.hook, name)
                if not hook.has_spec():
                    for hookimpl in hook.get_hookimpls():
                        if not hookimpl.optionalhook:
                            raise PluginValidationError(
                                hookimpl.plugin,
                                "unknown hook {!r} in plugin {!r}".format(name, hookimpl.plugin),
                            )

    def load_setuptools_entrypoints(self, group: str, name: str | None = None) -> int:
        """Load modules from querying the specified setuptools ``group``.

        :param group:
            Entry point group to load plugins.
        :param name:
            If given, loads only plugins with the given ``name``.

        :return:
            The number of plugins loaded by this call.
        """
        import importlib.metadata

        count = 0
        for dist in list(importlib.metadata.distributions()):
            for ep in dist.entry_points:
                if (
                    ep.group != group
                    or (name is not None and ep.name != name)
                    # already registered
                    or self.get_plugin(ep.name)
                    or self.is_blocked(ep.name)
                ):
                    continue
                # 加载
                plugin = ep.load()
                self.register(plugin, name=ep.name)
                self._plugin_distinfo.append((plugin, DistFacade(dist)))
                count += 1
        return count

    def add_hookcall_monitoring(self, before: _BeforeTrace, after: _AfterTrace) -> Callable[[], None]:
        """Add before/after tracing functions for all hooks.

        Returns an undo function which, when called, removes the added tracers.

        ``before(hook_name, hook_impls, kwargs)`` will be called ahead
        of all hook calls and receive a hookcaller instance, a list
        of HookImpl instances and the keyword arguments for the hook call.

        ``after(outcome, hook_name, hook_impls, kwargs)`` receives the
        same arguments as ``before`` but also a :class:`~pluggy.Result` object
        which represents the result of the overall hook call.
        """
        oldcall = self._inner_hookexec

        def traced_hookexec(
            hook_name: str,
            hook_impls: Sequence[HookImpl],
            caller_kwargs: Mapping[str, object],
            firstresult: bool,
        ) -> object | list[object]:
            # 前置操作
            before(hook_name, hook_impls, caller_kwargs)
            # 执行 hook
            outcome = Result.from_call(lambda: oldcall(hook_name, hook_impls, caller_kwargs, firstresult))
            # 后置操作
            after(outcome, hook_name, hook_impls, caller_kwargs)
            # 返回 hook
            return outcome.get_result()

        self._inner_hookexec = traced_hookexec

        def undo() -> None:
            self._inner_hookexec = oldcall

        return undo

    def enable_tracing(self) -> Callable[[], None]:
        """Enable tracing of hook calls.

        Returns an undo function which, when called, removes the added tracing.
        """
        hooktrace = self.trace.root.get("hook")

        def before(hook_name: str, methods: Sequence[HookImpl], kwargs: Mapping[str, object]) -> None:
            hooktrace.root.indent += 1
            hooktrace(hook_name, kwargs)

        def after(
            outcome: Result[object],
            hook_name: str,
            methods: Sequence[HookImpl],
            kwargs: Mapping[str, object],
        ) -> None:
            if outcome.exception is None:
                hooktrace("finish", hook_name, "-->", outcome.get_result())
            hooktrace.root.indent -= 1

        return self.add_hookcall_monitoring(before, after)

    def subset_hook_caller(self, name: str, remove_plugins: Iterable[_Plugin]) -> HookCaller:
        """Return a proxy :class:`~pluggy.HookCaller` instance for the named
        method which manages calls to all registered plugins except the ones
        from remove_plugins."""
        orig: HookCaller = getattr(self.hook, name)
        plugins_to_remove = {plug for plug in remove_plugins if hasattr(plug, name)}
        if plugins_to_remove:
            return SubsetHookCaller(orig, plugins_to_remove)
        return orig
