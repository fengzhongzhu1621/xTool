from enum import IntEnum, unique


@unique
class CodecType(IntEnum):
    DUMMY = 0

    JSON = 1
    YAML = 2
    URL_KV = 3

    PB = 10
    PB_JSON = 11
