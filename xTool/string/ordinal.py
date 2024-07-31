def find_ordinal(pos_num: int) -> str:
    # See: https://en.wikipedia.org/wiki/English_numerals#Ordinal_numbers
    if pos_num == 0:
        return "th"
    elif pos_num == 1:
        return "st"
    elif pos_num == 2:
        return "nd"
    elif pos_num == 3:
        return "rd"
    elif 4 <= pos_num <= 20:
        return "th"
    else:
        return find_ordinal(pos_num % 10)


def to_ordinal(pos_num: int) -> str:
    """将阿拉伯数字后面添加英文形容词后缀 ."""
    return f"{pos_num}{find_ordinal(pos_num)}"
