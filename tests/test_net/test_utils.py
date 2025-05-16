from xTool.net.ip import int_to_ipv4, ipv4_to_int, is_ipv4, is_ipv6


def test_int2ip():
    ip = "1.2.3.4"
    ip_int = ipv4_to_int(ip)
    actual = int_to_ipv4(ip_int)
    assert actual == ip


def test_is_ipv4():
    assert is_ipv4("1.1.1.1")
    assert not is_ipv4("1.1.1.1.1")
    assert not is_ipv4("1.1.1.1/24")


def test_is_ipv6():
    assert not is_ipv6("1.1.1.1")
    assert not is_ipv6("1.1.1.1.1")
    assert not is_ipv6("1.1.1.1/24")
    assert is_ipv6("2001:db8::1")
