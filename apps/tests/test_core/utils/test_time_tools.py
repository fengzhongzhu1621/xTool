from datetime import datetime

from core.utils import from_iso_format


def test_from_iso_format():
    """将iso8601格式的字符串转换为当前时区的时间对象 ."""
    start_time = "2023-01-01T00:00:00Z"
    actual = from_iso_format(start_time)
    expect = datetime(2023, 1, 1, 8, 0)
    assert actual == expect
