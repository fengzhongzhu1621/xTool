# -*- coding: utf-8 -*-

from builtins import object
from xTools import version
from xTools.utils.log.logging_mixin import LoggingMixin

__version__ = version.version

import sys

from xTools import configuration as conf
from xTools import settings
from xTools.exceptions import XToolsException
