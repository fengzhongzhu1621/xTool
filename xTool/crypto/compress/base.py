from enum import Enum, unique


@unique
class CompressType(Enum):
    DUMMY = 0

    ZLIB = 1
    BZ2 = 2
    GZIP = 3

    SNAPPY = 4
