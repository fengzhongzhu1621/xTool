from xTool.codec import count_md5, md5


def test_md5():
    assert md5("1") == "c4ca4238a0b923820dcc509a6f75849b"


def test_count_md5():
    actual = count_md5(["a", "b", "c"])
    expect = "89e0f7adc031c6238d095023a933c7a0"
    assert actual == expect

    actual = count_md5({"a": ["b", "c"]})
    expect = "c13d30900c448ecdbde696f3ab350276"
    assert actual == expect
