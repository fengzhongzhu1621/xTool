# -*- coding: utf-8 -*-


class XToolException(Exception):
    pass


class XToolConfigException(XToolException):
    pass


class XToolSensorTimeout(XToolException):
    pass


class XToolTaskTimeout(XToolException):
    pass


class XToolWebServerTimeout(XToolException):
    pass


class XToolSkipException(XToolException):
    pass


class XToolDagCycleException(XToolException):
    pass
