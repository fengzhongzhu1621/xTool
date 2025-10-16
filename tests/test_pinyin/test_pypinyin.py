from pypinyin import Style, lazy_pinyin, pinyin


def test_pinyin():
    actual = pinyin("我爱 python，我也爱 rust", style=Style.NORMAL)
    assert actual == [["wo"], ["ai"], [" python，"], ["wo"], ["ye"], ["ai"], [" rust"]]

    actual = pinyin("我爱 python，我也爱 rust", style=Style.TONE)
    assert actual == [["wǒ"], ["ài"], [" python，"], ["wǒ"], ["yě"], ["ài"], [" rust"]]

    actual = pinyin("我爱 python，我也爱 rust", style=Style.TONE2)
    assert actual == [["wo3"], ["a4i"], [" python，"], ["wo3"], ["ye3"], ["a4i"], [" rust"]]

    actual = pinyin("我爱 python，我也爱 rust", style=Style.TONE3)
    assert actual == [["wo3"], ["ai4"], [" python，"], ["wo3"], ["ye3"], ["ai4"], [" rust"]]


def test_lazy_pinyin():
    actual = lazy_pinyin("我爱 python，我也爱 rust")
    assert actual == ["wo", "ai", " python，", "wo", "ye", "ai", " rust"]
