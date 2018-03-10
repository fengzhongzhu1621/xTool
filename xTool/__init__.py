# -*- coding: utf-8 -*-

from builtins import object
from xTool import version
from xTool.utils.log.logging_mixin import LoggingMixin

__version__ = version.version

import sys

from xTool import configuration as conf
from xTool import settings
from xTool.exceptions import XToolException
