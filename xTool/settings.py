# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


LOGGING_LEVEL = logging.INFO

# the prefix to append to gunicorn worker processes after init
GUNICORN_WORKER_READY_PREFIX = "[ready] "


XTOOL_HOME = None
SQL_ALCHEMY_CONN = None


engine = None
Session = None
