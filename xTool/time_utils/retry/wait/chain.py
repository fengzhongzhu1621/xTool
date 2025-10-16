from typing import TYPE_CHECKING

from .base import wait_base

if TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "wait_chain",
]


class wait_chain(wait_base):
    """Chain two or more waiting strategies.

    If all strategies are exhausted, the very last strategy is used
    thereafter.

    For example::

        @retry(wait=wait_chain(*[wait_fixed(1) for i in range(3)] +
                               [wait_fixed(2) for j in range(5)] +
                               [wait_fixed(5) for k in range(4)))
        def wait_chained():
            print("Wait 1s for 3 attempts, 2s for 5 attempts and 5s
                   thereafter.")
    """

    def __init__(self, *strategies: wait_base) -> None:
        self.strategies = strategies

    def __call__(self, retry_state: "RetryCallState") -> float:
        # 从中选择一个等待策略执行，选择的策略与第几次调用有关
        wait_func_no = min(max(retry_state.attempt_number, 1), len(self.strategies))
        wait_func = self.strategies[wait_func_no - 1]
        return wait_func(retry_state=retry_state)
