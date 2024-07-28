from datetime import timedelta

from xTool.type_hint import time_unit_type


def to_seconds(time_unit: time_unit_type) -> float:
    return float(time_unit.total_seconds() if isinstance(time_unit, timedelta) else time_unit)
