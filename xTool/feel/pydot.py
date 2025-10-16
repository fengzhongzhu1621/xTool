from lark import Lark, tree


def make_png(parser: Lark, text: str, filename: str) -> None:
    tree.pydot__tree_to_png(parser.parse(text), filename)


def make_dot(parser: Lark, text: str, filename: str) -> None:
    tree.pydot__tree_to_dot(parser.parse(text), filename)


def make_pretty(parser: Lark, text: str) -> None:
    print(parser.parse(text).pretty())
