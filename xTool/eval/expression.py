# -*- coding: utf-8 -*-

from typing import Dict
from xTool.eval.constants import OP
from xTool.eval.operators import (Operator, BINARY_OPERATORS, AndOperator, OrOperator)


def make_expression(data: Dict) -> Operator:
    """创建一个表达式对象 ."""
    op = data["op"]

    if op == OP.AND:
        return AndOperator([make_expression(c) for c in data["content"]])
    elif op == OP.OR:
        return OrOperator([make_expression(c) for c in data["content"]])

    if op not in BINARY_OPERATORS:
        raise ValueError("operator %s not supported" % op)

    operator = BINARY_OPERATORS[op]

    field = data["field"]
    value = data["value"]

    return operator(field, value)
