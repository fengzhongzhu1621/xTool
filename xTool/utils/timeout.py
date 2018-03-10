# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import signal

from xTool.exceptions import XToolTaskTimeout
from xTool.utils.log.logging_mixin import LoggingMixin


class timeout(LoggingMixin):
    """超时上下文管理器: 给耗时操作增加统一的TimeOut超时处理机制（仅用于单进程）
    To be used in a ``with`` block and timeout its content.

    e.g. 
        try:
            with timeout(int(
                    task_copy.execution_timeout.total_seconds())):
                result = task_copy.execute(context=context)
        except XToolTaskTimeout:
            task_copy.on_kill()
            raise
    """

    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        self.log.error("Process timed out")
        raise XToolTaskTimeout(self.error_message)

    def __enter__(self):
        try:
            # 注册SIGLARM信号，延迟几秒后向自身进程发送信号
            # 进程收到信号后，抛出XToolTaskTimeout异常
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.seconds)
        except ValueError as e:
            self.log.warning("timeout can't be used in the current context")
            self.log.exception(e)

    def __exit__(self, type, value, traceback):
        try:
            # 关闭信号
            signal.alarm(0)
        except ValueError as e:
            self.log.warning("timeout can't be used in the current context")
            self.log.exception(e)
