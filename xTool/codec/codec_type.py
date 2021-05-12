# -*- coding: utf-8 -*-

from enum import unique, Enum


@unique
class CodecType(Enum):
    PICKLE = 1
    JSON = 2
    YAML = 3

    PB = 10
    PB_JSON = 11
