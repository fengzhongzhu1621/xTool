from typing import List

from django.db.models.query import QuerySet

__all__ = [
    "custom_sort_order",
]


def custom_sort_order(
    queryset: QuerySet,
    ordering_field: str,
    value_sequence: List,
) -> QuerySet:
    """
    根据指定的排序值的大小进行自定义排序 .

    数据表中一列如果是枚举类型，默认的排序方式是按照枚举类型的值从小到大进行排序，
    如果要自定义枚举类型的顺序，需要传入一个指定的顺序，按照传入的顺序进行排序

    :param queryset: 查询集
    :param ordering_field: 排序字段，只支持一个值排序
    :param value_sequence: 排序字段排序值列表, 可比较，从小到大
    """
    if not ordering_field:
        return queryset

    # 判断是否是逆序
    if ordering_field.startswith("-"):
        is_reverse = True
        ordering_field = ordering_field[1:]
    else:
        is_reverse = False

    # 将排序字段的值转换为 value_sequence 中的索引值
    clauses = " ".join(
        "WHEN {}='{}' THEN {} ".format(ordering_field, value if isinstance(value, int) else str(value), index)
        for index, value in enumerate(value_sequence)
    )
    ordering = "CASE %s END " % clauses

    # 将索引值作为排序字段
    if is_reverse:
        order_by = ("-ordering",)
    else:
        order_by = ("ordering",)
    queryset = queryset.extra(select={"ordering": ordering}, order_by=order_by)

    return queryset
