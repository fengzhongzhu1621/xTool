# -*- coding: utf-8 -*-

from enum import unique, Enum


@unique
class CompressType(Enum):
    DUMMY = 0

    ZLIB = 1
    BZ2 = 2
    GZIP = 3

    SNAPPY = 4
