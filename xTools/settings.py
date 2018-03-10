# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import pendulum

from xTool import configuration as conf


log = logging.getLogger(__name__)


TIMEZONE = pendulum.timezone('UTC')
try:
    tz = conf.get("core", "default_timezone")
    if tz == "system":
        TIMEZONE = pendulum.local_timezone()
    else:
        TIMEZONE = pendulum.timezone(tz)
except:
    pass
log.info("Configured default timezone %s" % TIMEZONE)