#coding: utf-8

from datetime import datetime
import functools

from xTool.utils.register_callback import *
from xTool.utils.log.logging_mixin import LoggingMixin


def default_action_1(log, **_):
    log.info("I'm default action pre 1")


def default_action_2(log, **_):
    log.info("I'm default action pre 2")


def default_action_3(log, **_):
    log.info("I'm default action post 1")


def default_action_4(log, **_):
    log.info("I'm default action post 2")


def action_logging(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        metrics = {}
        metrics['begin_datetime'] = datetime.now()
        metrics['end_datetime'] = None
        metrics['log']  = LoggingMixin().log
        on_pre_execution(**metrics)
        try:
            return f(*args, **kwargs)
        except Exception as e:
            metrics['error'] = e
            raise
        finally:
            metrics['end_datetime'] = datetime.now()
            on_post_execution(**metrics)

    return wrapper


def test_register_callback():
    register_pre_exec_callback(default_action_1)
    register_pre_exec_callback(default_action_2)
    register_post_exec_callback(default_action_3)
    register_post_exec_callback(default_action_4)

    @action_logging
    def action():
        pass
    action()
