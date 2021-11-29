# -*- coding: utf-8 -*-

from xTool.algorithms.collections.object import ObjectSet
from xTool.eval.expression import make_expression


def test_make_expression_and():
    d = {
        "op": "AND",
        "content": [
            {"op": "eq", "field": "host.id", "value": "a1"},
            {"op": "eq", "field": "host.name", "value": "b1"},
        ],
    }
    expr = make_expression(d)
    assert expr.expr() == "((host.id eq 'a1') AND (host.name eq 'b1'))"

    d1 = ObjectSet()
    d1.add_object("host", {"id": "a1", "name": "b1"})

    assert expr.eval(d1)


def test_make_expression_or():
    d = {
        "op": "OR",
        "content": [
            {"op": "eq", "field": "host.id", "value": "a1"},
            {"op": "eq", "field": "host.name", "value": "b1"},
        ],
    }
    expr = make_expression(d)
    assert expr.expr() == "((host.id eq 'a1') OR (host.name eq 'b1'))"

    d1 = ObjectSet()
    d1.add_object("host", {"id": "a1", "name": "b1"})

    assert expr.eval(d1)


def test_make_expression():
    d = {"op": "eq", "field": "host.id", "value": "a1"}
    expr = make_expression(d)

    assert expr.expr() == "(host.id eq 'a1')"

    d1 = ObjectSet()
    d1.add_object("host", {"id": "a1", "name": "b1"})

    assert expr.eval(d1)
