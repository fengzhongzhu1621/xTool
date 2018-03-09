# -*- coding: utf-8 -*-
#
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import sys
import warnings

import six

from builtins import object
from contextlib import contextmanager
from logging import Handler, StreamHandler


class LoggingMixin(object):
    """
    Convenience super-class to have a logger configured with the class name
    """

    def __init__(self, context=None):
        self._set_context(context)

    # We want to deprecate the logger property in Airflow 2.0
    # The log property is the de facto standard in most programming languages
    @property
    def logger(self):
        warnings.warn(
            'Initializing logger for {} using logger(), which will '
            'be replaced by .log in Airflow 2.0'.format(
                self.__class__.__module__ + '.' + self.__class__.__name__
            ),
            DeprecationWarning
        )
        return self.log

    @property
    def log(self):
        try:
            return self._log
        except AttributeError:
            self._log = logging.root.getChild(
                self.__class__.__module__ + '.' + self.__class__.__name__
            )
            return self._log

    def _set_context(self, context):
        if context is not None:
            set_context(self.log, context)


def set_context(logger, value):
    """
    Walks the tree of loggers and tries to set the context for each handler
    :param logger: logger
    :param value: value to set
    """
    _logger = logger
    while _logger:
        for handler in _logger.handlers:
            try:
                handler.set_context(value)
            except AttributeError:
                # Not all handlers need to have context passed in so we ignore
                # the error when handlers do not have set_context defined.
                pass
        if _logger.propagate is True:
            _logger = _logger.parent
        else:
            _logger = None
