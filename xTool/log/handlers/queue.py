import asyncio
import atexit
import logging
import queue
import sys
from contextlib import suppress
from logging.handlers import QueueHandler, QueueListener

from concurrent_log_handler.queue import get_all_logger_names, queuify_logger


def stop_queue_listeners(*listeners):
    for listener in listeners:
        with suppress(Exception):
            listener.stop()


class AsyncioQueueListener(QueueListener):
    def __init__(self, queue, *handlers, respect_handler_level=False):
        super().__init__(queue, *handlers, respect_handler_level=respect_handler_level)
        self.loop = None

    def _monitor(self):
        """
        Monitor the queue for records, and ask the handler
        to deal with them.

        This method runs on a separate, internal thread.
        The thread will terminate if it sees a sentinel object in the queue.
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        q = self.queue
        has_task_done = hasattr(q, "task_done")
        while True:
            try:
                record = self.dequeue(True)
                if record is self._sentinel:
                    break
                self.handle(record)
                if has_task_done:
                    q.task_done()
            except queue.Empty:
                break

    def stop(self):
        super().stop()
        if self.loop:
            self.loop.stop()


def setup_logging_asyncio_queue_listener():
    if sys.version_info.major < 3:
        raise RuntimeError("This feature requires Python 3.")

    queue_listeners = []

    # Q: What about loggers created after this is called?
    # A: if they don't attach their own handlers they should be fine
    for logger in get_all_logger_names(include_root=True):
        logger = logging.getLogger(logger)
        if logger.handlers:
            log_queue = queue.Queue(-1)  # No limit on size

            queue_handler = QueueHandler(log_queue)
            queue_listener = AsyncioQueueListener(log_queue, respect_handler_level=True)
            # 将所有的handers绑定到queue_listener，然后将logger.handlers清空并设置为queue_handler
            queuify_logger(logger, queue_handler, queue_listener)
            queue_listeners.append(queue_listener)

    for listener in queue_listeners:
        listener.start()

    atexit.register(stop_queue_listeners, *queue_listeners)
    return
