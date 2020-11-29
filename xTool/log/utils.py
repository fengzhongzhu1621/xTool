# -*- coding: utf-8 -*-

import logging


def get_all_logger_names(include_root=False):
    """Return ``list`` of names of all loggers than have been accessed.

    Warning: this is sensitive to internal structures in the standard logging module.
    """
    # noinspection PyUnresolvedReferences
    logger_keys = list(logging.Logger.manager.loggerDict.keys())
    if include_root:
        logger_keys.insert(0, '')
    return logger_keys


def fix_logging_module_after_fork_in_child():
    logger_keys = list(logging.Logger.manager.loggerDict.keys())
    logger_keys.insert(0, '')

    for logger_name in logger_keys:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            # 使用新的锁，因为fork后的子进程如果还是用父进程的锁，子进程会获取不到锁
            handler.createLock()
