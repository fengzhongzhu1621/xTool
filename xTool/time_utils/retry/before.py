import typing

from xTool.inspect_utils.callback import get_callback_name
from xTool.string.ordinal import to_ordinal

if typing.TYPE_CHECKING:
    import logging

    from xTool.time_utils.retry.state import RetryCallState


def before_nothing(retry_state: "RetryCallState") -> None:
    """Before call strategy that does nothing."""


def before_log(logger: "logging.Logger", log_level: int) -> typing.Callable[["RetryCallState"], None]:
    """Before call strategy that logs to some logger the attempt，执行前打印日志 ."""

    def log_it(retry_state: "RetryCallState") -> None:
        fn_name = get_callback_name(retry_state.fn)
        logger.log(
            log_level,
            f"Starting call to '{fn_name}', " f"this is the {to_ordinal(retry_state.attempt_number)} time calling it.",
        )

    return log_it
