# -*- coding: utf-8 -*-

from enum import unique, IntEnum


@unique
class ConfigLoaderType(IntEnum):
    FILE = 1
