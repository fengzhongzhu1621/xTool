# -*- coding: utf-8 -*-

from enum import unique, Enum


@unique
class ConfigLoaderType(Enum):
    FILE = 1
