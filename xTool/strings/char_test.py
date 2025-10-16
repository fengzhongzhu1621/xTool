from xTool.strings.char import get_chr_seq


def test_get_chr_seq():
    # 生成小写字母 a-z
    get_chr_seq('a', 'z') == ['a', 'b', 'c', ..., 'z']

    # 生成大写字母 A-Z
    get_chr_seq('A', 'Z') == ['A', 'B', 'C', ..., 'Z']

    # 生成数字字符 0-9
    get_chr_seq('0', '9') == ['0', '1', '2', ..., '9']

    # 生成特殊字符序列（如 '!' 到 '/'）
    get_chr_seq('!', '/') == [
        '!',
        '"',
        '#',
        '$',
        '%',
        '&',
        "'",
        '(',
        ')',
        '*',
        '+',
        ',',
        '-',
        '.',
        '/',
    ]
