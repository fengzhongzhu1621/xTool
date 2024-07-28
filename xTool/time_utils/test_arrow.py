import arrow


def test_replace():
    now = arrow.utcnow().to("Asia/Shanghai")
    actual = now.replace(year=2024, month=7, day=15, hour=14, minute=0, second=0).format()
    expect = "2024-07-15 14:00:00+08:00"
    assert actual == expect
