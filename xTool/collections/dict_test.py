from xTool.collections.dict import distinct_dict_list


def test_distinct_dict_list():
    assert distinct_dict_list([]) == []

    assert distinct_dict_list(
        [{'a': 1, 'b': 2}, {'b': 2, 'a': 1}, {'c': 3, 'd': 4}, {'a': 1, 'b': 2}]  # 和第一个字典相同（顺序不同）  # 重复
    ) == [
        {'a': 1, 'b': 2},
        {'c': 3, 'd': 4},
    ]

    assert distinct_dict_list([{'a': 1}, {'a': 1}, {'a': 1}]) == [{'a': 1}]
    assert distinct_dict_list(
        [{'a': 1, 'b': (2, 3)}, {'a': 1, 'b': [2, 3]}]  # (2, 3) 是不可变元组  # [2, 3] 是可变列表（会报错！）
    ) == [{'a': 1, 'b': (2, 3)}]
