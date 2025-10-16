from xpinyin import Pinyin


def test_get_pinyin():
    p = Pinyin()
    actual = p.get_pinyin("中国", tone_marks=True)
    assert actual == "zhong1-guo2"

    actual = p.get_pinyin("上海", tone_marks="marks")
    assert actual == "shàng-hǎi"

    actual = p.get_pinyin("上海", tone_marks="numbers")
    assert actual == "shang4-hai3"

    actual = p.get_pinyin("上海", "")
    expect = "shanghai"
    assert actual == expect

    actual = p.get_pinyin("上海", " ")
    expect = "shang hai"
    assert actual == expect


def test_get_initials():
    p = Pinyin()
    actual = p.get_initials("上海")
    expect = "S-H"
    assert actual == expect

    actual = p.get_initials("上海", " ")
    expect = "S H"
    assert actual == expect

    actual = p.get_initials("上海", splitter="-", with_retroflex=True)
    expect = "SH-H"
    assert actual == expect

    actual = p.get_pinyins("模型", splitter=" ", tone_marks="marks")
    expect = ["mó xíng", "mú xíng"]
    assert actual == expect

    actual = p.get_pinyins("模样", splitter=" ", tone_marks="marks")
    expect = ["mó yáng", "mó yàng", "mó xiàng", "mú yáng", "mú yàng", "mú xiàng"]
    assert actual == expect
