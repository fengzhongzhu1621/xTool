"""
Basic calculator
================

A simple example of a REPL calculator

This example shows how to write a basic calculator with variables.
"""

import operator

from lark import Lark, Transformer, v_args

calc_grammar = """
    ?start: sum
          | NAME "=" sum    -> assign_var

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"

    // 第一个字符下划或大小写字母，其余字符是大小写字母
    %import common.CNAME -> NAME
    // 正数
    %import common.NUMBER
    %import common.WS_INLINE

    // 忽略空格和制表符
    %ignore WS_INLINE
"""


@v_args(inline=True)  # Affects the signatures of the methods
class CalculateTree(Transformer):
    number = float

    def __init__(self):
        self.vars = {}

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        try:
            return self.vars[name]
        except KeyError:
            raise Exception("Variable not found: %s" % name)

    add = operator.add
    sub = operator.sub
    mul = operator.mul
    div = operator.floordiv
    neg = operator.neg


calc = Lark(calc_grammar, parser="lalr", transformer=CalculateTree()).parse


def test_calc():
    assert calc("a = 1+2") == 3
    assert calc("1+a*-3") == -8.0
    assert calc("2*(3+4)") == 14.0
