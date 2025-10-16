import idna


def test_encode():
    actual = idna.encode("www.中文域名.com")
    expect = b"www.xn--fiq06l2rdsvs.com"
    assert actual == expect
