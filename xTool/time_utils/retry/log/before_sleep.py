import typing

from xTool.inspect_utils.callback import get_callback_name

if typing.TYPE_CHECKING:
    import logging

    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "before_sleep_nothing",
    "before_sleep_log",
]


def before_sleep_nothing(retry_state: "RetryCallState") -> None:
    """Before call strategy that does nothing."""


def before_sleep_log(
    logger: "logging.Logger",
    log_level: int,
    exc_info: bool = False,
) -> typing.Callable[["RetryCallState"], None]:
    """Before call strategy that logs to some logger the attempt，重试任务前打印上一次执行的结果和与下一次执行的间隔（包括失败异常或正常执行结果） ."""

    # RetryCallState 表示重试前的状态
    def log_it(retry_state: "RetryCallState") -> None:
        local_exc_info: BaseException | bool | None

        # 上次任务没有执行完成或未执行，即状态机的节点没有入度
        if retry_state.outcome is None:
            raise RuntimeError("log_it() called before outcome was set")

        if retry_state.next_action is None:
            raise RuntimeError("log_it() called before next_action was set")

        # 判断上一次执行是否失败
        if retry_state.outcome.failed:
            # 失败则获得上一次异常原因
            ex = retry_state.outcome.exception()
            verb, value = "raised", f"{ex.__class__.__name__}: {ex}"

            if exc_info:
                local_exc_info = ex
            else:
                local_exc_info = False
        else:
            # 成功则获得上一次的执行结果
            verb, value = "returned", retry_state.outcome.result()
            local_exc_info = False  # exc_info does not apply when no exception

        fn_name = get_callback_name(retry_state.fn)

        # 记录重试的原因（不管成功或失败都有重试的场景）
        logger.log(
            log_level,
            f"Retrying {fn_name} " f"in {retry_state.next_action.sleep} seconds as it {verb} {value}.",
            exc_info=local_exc_info,
        )

    return log_it
