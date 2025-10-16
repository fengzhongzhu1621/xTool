from collections import Counter
from typing import List, Set, Union


def compare_list(
    left: Union[List[Union[str, int]], Set[Union[str, int]]],
    right: Union[List[Union[str, int]], Set[Union[str, int]]],
    use_sort=True,
) -> bool:
    """
    判断列表是否相等，支持具有重复值列表的比较
    参考：https://stackoverflow.com/questions/9623114/check-if-two-unordered-lists-are-equal
    :param left:
    :param right:
    :param use_sort: 使用有序列表可比较的特性，数据规模不大的情况下性能优于Counter
    :return:
    """
    if isinstance(left, set) and isinstance(right, set):
        return left == right

    # 适用于小规模数据，因为排序的时间复杂度是 O(nlogn)。
    if use_sort:
        return sorted(list(left)) == sorted(list(right))

    # 使用 collections.Counter 统计每个元素的出现次数，然后比较计数器是否相等。
    # 适用于大规模数据，因为 Counter 的时间复杂度是 O(n)，但需要额外空间存储计数。
    return Counter(left) == Counter(right)
