import typing

from xTool.inspect_utils.callback import get_callback_name
from xTool.strings.ordinal import to_ordinal

if typing.TYPE_CHECKING:
    import logging

    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "after_nothing",
    "after_log",
]


def after_nothing(retry_state: "RetryCallState") -> None:
    """After call strategy that does nothing."""


def after_log(
    logger: "logging.Logger",
    log_level: int,
    sec_format: str = "%0.3f",
) -> typing.Callable[["RetryCallState"], None]:
    """After call strategy that logs to some logger the finished attempt，重试任务后打印耗时日志 ."""

    # 表示重试后的状态
    def log_it(retry_state: "RetryCallState") -> None:
        fn_name = get_callback_name(retry_state.fn)
        logger.log(
            log_level,
            f"Finished call to '{fn_name}' "
            f"after {sec_format % retry_state.seconds_since_start}(s), "
            f"this was the {to_ordinal(retry_state.attempt_number)} time calling it.",
        )

    return log_it
