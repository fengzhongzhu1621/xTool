# -*- coding: utf-8 -*-

from __future__ import absolute_import

import warnings

from .decorators import apply_defaults as _apply_defaults


def apply_defaults(func):
    warnings.warn_explicit(
        """
        You are importing apply_defaults from airflow.utils which
        will be deprecated in a future version.
        Please use :

        from xTool.utils.decorators import apply_defaults
        """,
        category=PendingDeprecationWarning,
        filename=func.__code__.co_filename,
        lineno=func.__code__.co_firstlineno + 1
    )
    return _apply_defaults(func)
