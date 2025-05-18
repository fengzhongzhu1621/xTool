from xTool.number.consecutive import is_consecutive_strings


def test_is_consecutive_strings():
    assert is_consecutive_strings(["1", "2", "3"]) is True
    assert is_consecutive_strings(["3", "2", "1"]) is True
    assert is_consecutive_strings(["1", "3", "4"]) is False
    assert is_consecutive_strings(["1"]) is True
    assert is_consecutive_strings([]) is False
    assert is_consecutive_strings(["a", "b"]) is False
    assert is_consecutive_strings(["10", "11", "12", "14"]) is False
