from typing import Generator, Mapping, NoReturn, Sequence, Tuple, Union, cast

from .exceptions import HookCallError
from .hookimpl_marker import HookImpl
from .result import Result

# Need to distinguish between old- and new-style hook wrappers.
# Wrapping with a tuple is the fastest type-safe way I found to do it.
Teardown = Union[
    Tuple[Generator[None, Result[object], None], HookImpl],
    Generator[None, object, object],
]


def _raise_wrapfail(
    wrap_controller: Generator[None, Result[object], None] | Generator[None, object, object],
    msg: str,
) -> NoReturn:
    co = wrap_controller.gi_code
    raise RuntimeError("wrap_controller at %r %s:%d %s" % (co.co_name, co.co_filename, co.co_firstlineno, msg))


def multicall(
    hook_name: str,
    hook_impls: Sequence[HookImpl],  # 一个包含 HookImpl 对象的序列，这些对象代表了要调用的函数或方法
    caller_kwargs: Mapping[str, object],  # 从 HookCaller.__call__() 方法传递过来的关键字参数。
    firstresult: bool,  # 一个布尔值，如果为 True，则只返回第一个结果；如果为 False，则返回所有结果。
) -> object | list[object]:
    """Execute a call into multiple python functions/methods and return the
    result(s). 执行钩子实现.

    ``caller_kwargs`` comes from HookCaller.__call__().
    """
    __tracebackhide__ = True
    results: list[object] = []
    exception = None

    try:  # run impl and wrapper setup functions in a loop
        teardowns: list[Teardown] = []
        try:
            # 逆序执行，最后添加的钩子实现先执行
            for hook_impl in reversed(hook_impls):
                # 获得钩子实现的位置参数的值
                try:
                    args = [caller_kwargs[argname] for argname in hook_impl.argnames]
                except KeyError:
                    for argname in hook_impl.argnames:
                        if argname not in caller_kwargs:
                            raise HookCallError(f"hook call must provide argument {argname!r}")

                if hook_impl.wrapper:
                    try:
                        # If this cast is not valid, a type error is raised below,
                        # which is the desired response.
                        res = hook_impl.function(*args)
                        function_gen = cast(Generator[None, object, object], res)
                        # 启动生成器
                        next(function_gen)  # first yield
                        teardowns.append(function_gen)
                    except StopIteration:
                        _raise_wrapfail(function_gen, "did not yield")
                else:
                    res = hook_impl.function(*args)
                    # 钩子实现返回 None，不收集结果
                    if res is not None:
                        results.append(res)
                        if firstresult:  # halt further impl calls
                            # 只返回第一个钩子实现的结果
                            break
        except BaseException as exc:
            # 异常则终止后续的钩子实现的执行
            exception = exc
    finally:
        if firstresult:  # first result hooks return a single value
            result = results[0] if results else None
        else:
            result = results

        # run all wrapper post-yield blocks
        for teardown in reversed(teardowns):
            try:
                if exception is not None:
                    teardown.throw(exception)  # type: ignore[union-attr]
                else:
                    # 将已执行的 hooks 的所有结果传递给当前 hook 执行
                    teardown.send(result)  # type: ignore[union-attr]
                # Following is unreachable for a well behaved hook wrapper.
                # Try to force finalizers otherwise postponed till GC action.
                # Note: close() may raise if generator handles GeneratorExit.
                teardown.close()  # type: ignore[union-attr]
            except StopIteration as si:
                # 获得当前 hook 的执行结果
                result = si.value
                exception = None
                continue
            except BaseException as e:
                exception = e
                continue
            _raise_wrapfail(teardown, "has second yield")  # type: ignore[arg-type]

        if exception is not None:
            raise exception
        else:
            return result
