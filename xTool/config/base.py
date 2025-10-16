from enum import IntEnum, unique


@unique
class ConfigLoaderType(IntEnum):
    FILE = 1
