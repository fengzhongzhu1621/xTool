# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging


def register_pre_exec_callback(action):
    """
    Registers more action function callback for pre-execution.
    This function callback is expected to be called with keyword args.
    For more about the arguments that is being passed to the callback,
    refer to airflow.utils.cli.action_logging()
    :param action: An action logger function
    :return: None
    """
    logging.debug("Adding {} to pre execution callback".format(action))
    __pre_exec_callbacks.append(action)


def register_post_exec_callback(action):
    """
    Registers more action function callback for post-execution.
    This function callback is expected to be called with keyword args.
    For more about the arguments that is being passed to the callback,
    refer to airflow.utils.cli.action_logging()
    :param action: An action logger function
    :return: None
    """
    logging.debug("Adding {} to post execution callback".format(action))
    __post_exec_callbacks.append(action)


def on_pre_execution(**kwargs):
    """
    Calls callbacks before execution.
    Note that any exception from callback will be logged but won't be propagated.
    :param kwargs:
    :return: None
    """
    logging.debug("Calling callbacks: {}".format(__pre_exec_callbacks))
    for action in __pre_exec_callbacks:
        try:
            action(**kwargs)
        except Exception:
            logging.exception('Failed on pre-execution callback using {}'.format(action))


def on_post_execution(**kwargs):
    """
    Calls callbacks after execution.
    As it's being called after execution, it can capture status of execution,
    duration, etc. Note that any exception from callback will be logged but
    won't be propagated.
    :param kwargs:
    :return: None
    """
    logging.debug("Calling callbacks: {}".format(__post_exec_callbacks))
    for action in __post_exec_callbacks:
        try:
            action(**kwargs)
        except Exception:
            logging.exception('Failed on post-execution callback using {}'.format(action))


__pre_exec_callbacks = []
__post_exec_callbacks = []
