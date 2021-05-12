# -*- coding: utf-8 -*-

from enum import unique, Enum


@unique
class CodecType(Enum):
    PICKLE = 1
    JSON = 2
    PB = 3
    PB_JSON = 4
