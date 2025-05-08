from enum import Enum, unique

__all__ = ["TimeEnum"]


@unique
class TimeEnum(Enum):
    """
    时间枚举
    """

    ONE_SECOND: int = 1
    HALF_MINUTE_SECOND: int = ONE_SECOND * 30
    ONE_MINUTE_SECOND: int = ONE_SECOND * 60
    FIVE_MINUTE_SECOND: int = ONE_MINUTE_SECOND * 5
    TEN_MINUTE_SECOND: int = ONE_MINUTE_SECOND * 10
    HALF_HOUR_SECOND: int = ONE_MINUTE_SECOND * 30
    ONE_HOUR_SECOND: int = ONE_MINUTE_SECOND * 60
    ONE_DAY_SECOND: int = ONE_HOUR_SECOND * 24
    ONE_YEAR_SECOND: int = ONE_DAY_SECOND * 365
    SEVEN_DAY_SECONDS: int = ONE_DAY_SECOND * 7
