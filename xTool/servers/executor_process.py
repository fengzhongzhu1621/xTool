# -*- coding: utf-8 -*-

import asyncio
import multiprocessing


class ExecutorProcess(multiprocessing.Process):
    def __init__(self, *args, **kwargs):
        self.loop = None
        super().__init__(*args, **kwargs)

    def run(self):
        # 子进程使用自己的事件处理流
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
