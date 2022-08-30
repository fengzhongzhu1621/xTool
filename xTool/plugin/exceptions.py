# -*- coding: utf-8 -*-

from xTool.exceptions import XToolException


class PluginException(XToolException):
    pass


class PluginTypeNotFound(PluginException):
    pass


class PluginHaveInstalled(PluginException):
    pass
