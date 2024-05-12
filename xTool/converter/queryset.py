import operator

from django.db.models import Q
from six.moves import reduce

from xTool.converter.base import Converter
from xTool.eval.constants import OP

"""
表达式解析

convert expression to django queryset
"""


class DjangoQuerySetConverter(Converter):
    def __init__(self, key_mapping=None, value_hooks=None):
        super().__init__(key_mapping)

        self.value_hooks = value_hooks or {}

    def _positive(self, fmt, left, right):
        is_array = isinstance(right, (list, tuple))
        if is_array:
            kwargs_list = [{fmt.format(left): r} for r in right]
            return reduce(operator.or_, [Q(**kw) for kw in kwargs_list])

        kwargs = {fmt.format(left): right}
        return Q(**kwargs)

    def _negative(self, fmt, left, right):
        is_array = isinstance(right, (list, tuple))
        if is_array:
            kwargs_list = [{fmt.format(left): r} for r in right]
            return reduce(operator.and_, [~Q(**kw) for kw in kwargs_list])

        kwargs = {fmt.format(left): right}
        return ~Q(**kwargs)

    def _eq(self, left, right):
        return self._positive("{}", left, right)

    def _not_eq(self, left, right):
        return self._negative("{}", left, right)

    def _in(self, left, right):
        kwargs = {"{}__in".format(left): right}
        return Q(**kwargs)

    def _not_in(self, left, right):
        kwargs = {"{}__in".format(left): right}
        return ~Q(**kwargs)

    def _contains(self, left, right):
        return self._positive("{}__contains", left, right)

    def _not_contains(self, left, right):
        return self._negative("{}__contains", left, right)

    def _starts_with(self, left, right):
        return self._positive("{}__startswith", left, right)

    def _not_starts_with(self, left, right):
        return self._negative("{}__startswith", left, right)

    def _ends_with(self, left, right):
        return self._positive("{}__endswith", left, right)

    def _not_ends_with(self, left, right):
        return self._negative("{}__endswith", left, right)

    def _lt(self, left, right):
        return self._positive("{}__lt", left, right)

    def _lte(self, left, right):
        return self._positive("{}__lte", left, right)

    def _gt(self, left, right):
        return self._positive("{}__gt", left, right)

    def _gte(self, left, right):
        return self._positive("{}__gte", left, right)

    def _any(self, left, right):
        # https://stackoverflow.com/questions/33517468/always-true-q-object
        # ~Q(pk__in=[]) => not in? should check the sql/performance

        # NOTE: We think the pk is not null in mysql schema here
        return ~Q(pk=None)

    def _and(self, content):
        # print("in _and we got", [self.convert(c) for c in content])
        return reduce(operator.and_, [self.convert(c) for c in content])

    def _or(self, content):
        # print("in _or we got", [self.convert(c) for c in content])
        return reduce(operator.or_, [self.convert(c) for c in content])

    def operator_map(self, operator, field, value):
        return None

    def convert(self, data):
        op = data["op"]

        if op == OP.AND:
            return self._and(data["content"])
        elif op == OP.OR:
            return self._or(data["content"])

        value = data["value"]
        field = data["field"]

        op_func = self.operator_map(op, field, value)

        if not op_func:
            op_func = {
                OP.EQ: self._eq,
                OP.NOT_EQ: self._not_eq,
                OP.IN: self._in,
                OP.NOT_IN: self._not_in,
                OP.CONTAINS: self._contains,
                OP.NOT_CONTAINS: self._not_contains,
                OP.STARTS_WITH: self._starts_with,
                OP.NOT_STARTS_WITH: self._not_starts_with,
                OP.ENDS_WITH: self._ends_with,
                OP.NOT_ENDS_WITH: self._not_ends_with,
                OP.LT: self._lt,
                OP.LTE: self._lte,
                OP.GT: self._gt,
                OP.GTE: self._gte,
                OP.ANY: self._any,
            }.get(op)

        if op_func is None:
            raise ValueError("invalid op %s" % op)

        # key mapping
        if self.key_mapping and field in self.key_mapping:
            field = self.key_mapping.get(field)
        # value hooks
        if (field in self.value_hooks) and callable(self.value_hooks[field]):
            value = self.value_hooks[field](value)

        return op_func(field, value)
