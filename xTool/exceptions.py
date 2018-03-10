# -*- coding: utf-8 -*-


class XToolException(Exception):
    pass


class XToolConfigException(XToolException):
    pass

class XToolTaskTimeout(XToolException):
    pass
