from typing import Dict

from lark import Lark

from .transformer import FEELTransformer


def parse_expression(expr: str, context: Dict):
    tree = Lark.open("FEEL.lark", rel_to=__file__, parser="lalr").parse(expr.strip())
    ast = FEELTransformer().transform(tree)
    result = ast.evaluate(context or {})

    return result
