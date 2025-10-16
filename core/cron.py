from datetime import datetime, timedelta
from typing import List, Optional, Union

from croniter import croniter
from django.utils import timezone


class Cron:
    """定时任务表达式处理器 ."""

    def __init__(self, expression: str) -> None:
        # cron 表达式
        self.expression = expression

    def get_next(self, start_time: Optional[datetime] = None) -> datetime:
        """获得下一个调度时间 ."""
        # 去掉时区
        if start_time and not timezone.is_naive(start_time):
            start_time = timezone.make_naive(start_time)

        # 获得下一个调度时间
        if start_time:
            cron = croniter(self.expression, start_time=start_time)
        else:
            cron = croniter(self.expression)
        scheduled = cron.get_next(datetime)

        # 添加时区
        result = timezone.make_aware(scheduled)

        return result

    def get_prev(self, start_time: Optional[datetime]) -> datetime:
        """获得上一个调度时间 ."""
        # 去掉时区
        if not timezone.is_naive(start_time):
            start_time = timezone.make_naive(start_time)

        # 获得上一个调度时间
        cron = croniter(self.expression, start_time=start_time)
        prev = cron.get_prev(datetime)

        # 添加时区
        if prev == start_time:
            result = timezone.make_aware(start_time)
        else:
            result = timezone.make_aware(prev)

        return result


def date_range(
    start_date: datetime,
    end_date: Optional[datetime] = None,
    num: Optional[int] = None,
    delta: Union[str, timedelta, None] = None,
) -> List[datetime]:
    """获得时间范围 ."""
    # 验证输入参数
    if not delta:
        return []
    if end_date:
        if start_date > end_date:
            raise Exception("Wait. start_date needs to be before end_date")
        if num:
            raise Exception("Wait. Either specify end_date OR num")
    if not end_date and not num:
        end_date = timezone.now()

    delta_is_cron = False
    time_zone = start_date.tzinfo

    # 格式化输入参数
    abs_delta: timedelta
    if isinstance(delta, str):
        delta_is_cron = True
        if not timezone.is_naive(start_date):
            start_date = timezone.make_naive(start_date, time_zone)
        cron = croniter(delta, start_date)
    elif isinstance(delta, timedelta):
        abs_delta = abs(delta)
    else:
        raise Exception("Wait. delta must be either datetime.timedelta or cron expression as str")

    dates = []
    if end_date:
        if timezone.is_naive(start_date) and not timezone.is_naive(end_date):
            # 去掉时区
            end_date = timezone.make_naive(end_date, time_zone)
        # 根据结束时间获得时间范围
        while start_date <= end_date:  # type: ignore
            if timezone.is_naive(start_date):
                dates.append(timezone.make_aware(start_date, time_zone))
            else:
                dates.append(start_date)

            if delta_is_cron:
                start_date = cron.get_next(datetime)
            else:
                start_date += abs_delta
    else:
        # 根据周期数获得时间范围
        num_entries: int = num  # type: ignore
        for _ in range(abs(num_entries)):
            if timezone.is_naive(start_date):
                dates.append(timezone.make_aware(start_date, time_zone))
            else:
                dates.append(start_date)

            if delta_is_cron and num_entries > 0:
                start_date = cron.get_next(datetime)
            elif delta_is_cron:
                start_date = cron.get_prev(datetime)
            elif num_entries > 0:
                start_date += abs_delta
            else:
                start_date -= abs_delta

    return sorted(dates)
