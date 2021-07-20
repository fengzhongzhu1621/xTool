# -*- coding: utf-8 -*-

from enum import unique, IntEnum


@unique
class CodecType(IntEnum):
    DUMMY = 0

    PICKLE = 1
    JSON = 2
    YAML = 3
    URL_KV = 4

    PB = 10
    PB_JSON = 11
