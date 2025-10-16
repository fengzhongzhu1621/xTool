from lark import Lark, Token, Transformer, Tree

json_parser = Lark(
    """
    value: dict
         | list
         | ESCAPED_STRING
         | SIGNED_NUMBER
         | "true" | "false" | "null"

    list : "[" [value ("," value)*] "]"

    dict : "{" [pair ("," pair)*] "}"
    pair : ESCAPED_STRING ":" value

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
""",
    start="value",
)

json_parser_2 = Lark(
    r"""
    ?value: dict
         | list
         | string
         | SIGNED_NUMBER  -> number
         | "true"  -> true
         | "false" -> false
         | "null"  -> null

    list: "[" [value ("," value)*] "]"

    dict: "{" [pair ("," pair)*] "}"
    pair: string ":" value

    string: ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
    """,
    start="value",
)

json_parser_3 = Lark(
    r"""
    value: dict
         | list
         | string
         | SIGNED_NUMBER  -> number
         | "true"  -> true
         | "false" -> false
         | "null"  -> null

    list: "[" [value ("," value)*] "]"

    dict: "{" [pair ("," pair)*] "}"
    pair: string ":" value

    string: ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
    """,
    start="value",
)


class MyTransformer(Transformer):
    def list(self, items):
        return list(items)

    def pair(self, key_value):
        k, v = key_value
        return k, v

    def dict(self, items):
        return dict(items)


class TreeToJson(Transformer):
    def string(self, s):
        (value,) = s
        return value[1:-1]

    def number(self, n):
        (value,) = n
        return float(value)

    list = list
    pair = tuple
    dict = dict

    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False


def test_parse_simple():
    lark_obj = Lark(
        """
start: WORD "," WORD "!"

%import common.WORD   // imports from terminal library
%ignore " "           // 忽略文本中的空格
""".strip()
    )

    tree = lark_obj.parse("Hello, World!")

    expect = Tree(Token("RULE", "start"), [Token("WORD", "Hello"), Token("WORD", "World")])
    assert tree == expect


def test_parse_json_simple():
    text = '{"key": ["item0", "item1", 3.14, true]}'
    parser = json_parser.parse(text)
    expect = Tree(
        Token("RULE", "value"),
        [
            Tree(
                Token("RULE", "dict"),
                [
                    Tree(
                        Token("RULE", "pair"),
                        [
                            Token("ESCAPED_STRING", '"key"'),
                            Tree(
                                Token("RULE", "value"),
                                [
                                    Tree(
                                        Token("RULE", "list"),
                                        [
                                            Tree(
                                                Token("RULE", "value"),
                                                [Token("ESCAPED_STRING", '"item0"')],
                                            ),
                                            Tree(
                                                Token("RULE", "value"),
                                                [Token("ESCAPED_STRING", '"item1"')],
                                            ),
                                            Tree(
                                                Token("RULE", "value"),
                                                [Token("SIGNED_NUMBER", "3.14")],
                                            ),
                                            Tree(Token("RULE", "value"), []),
                                        ],
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            )
        ],
    )
    assert parser == expect

    expect = """
value
  dict
    pair
      "key"
      value
        list
          value	"item0"
          value	"item1"
          value	3.14
          value
""".lstrip()
    assert parser.pretty() == expect


def test_parse_json_2():
    # 箭头 (->) 表示别名 alias。别名是规则特定部分的名称。 在本例中命名匹配的 true/false/null，不会丢失信息。 同时也命名 SIGNED_NUMBER 方便后续处理。
    # value 前的问号 (?value) 告诉树生成器在只有一个成员的情况下将该分支内联 (inline)。 在本例中，value 只可能有一个成员，所以总会被内联。
    # 将 terminal ESCAPED_STRING 变为 rule，会在树中表示为分支。 与 alias 等价，但 string 也可以用在语法的其它地方。
    text = '{"key": ["item0", "item1", 3.14, true]}'
    parser = json_parser_2.parse(text)
    expect = Tree(
        Token("RULE", "dict"),
        [
            Tree(
                Token("RULE", "pair"),
                [
                    Tree(Token("RULE", "string"), [Token("ESCAPED_STRING", '"key"')]),
                    Tree(
                        Token("RULE", "list"),
                        [
                            Tree(
                                Token("RULE", "string"),
                                [Token("ESCAPED_STRING", '"item0"')],
                            ),
                            Tree(
                                Token("RULE", "string"),
                                [Token("ESCAPED_STRING", '"item1"')],
                            ),
                            Tree("number", [Token("SIGNED_NUMBER", "3.14")]),
                            Tree("true", []),
                        ],
                    ),
                ],
            )
        ],
    )
    assert parser == expect

    # 可以看到 value 被内联，true 被正常识别，字符串 (string) 和数字 (number) 都有使用了别名
    expect = """
dict
  pair
    string	"key"
    list
      string	"item0"
      string	"item1"
      number	3.14
      true
""".lstrip()
    assert parser.pretty() == expect

    # 评估结构树
    # 转换器是一个类，类方法对应分支名。 对于每个分支，相应的方法会被调用，将分支的子节点作为参数，返回值会替换树中的分支。
    transform_tree = MyTransformer().transform(parser)
    expect = {
        Tree(Token("RULE", "string"), [Token("ESCAPED_STRING", '"key"')]): [
            Tree(Token("RULE", "string"), [Token("ESCAPED_STRING", '"item0"')]),
            Tree(Token("RULE", "string"), [Token("ESCAPED_STRING", '"item1"')]),
            Tree("number", [Token("SIGNED_NUMBER", "3.14")]),
            Tree("true", []),
        ]
    }
    assert transform_tree == expect

    transform_tree = TreeToJson().transform(parser)
    expect = {"key": ["item0", "item1", 3.14, True]}
    assert transform_tree == expect


def test_parse_json_3():
    """测试 value 不内连 ."""
    text = '{"key": ["item0", "item1", 3.14, true]}'
    parser = json_parser_3.parse(text)
    expect = (
        "value\n"
        "  dict\n"
        "    pair\n"
        '      string\t"key"\n'
        "      value\n"
        "        list\n"
        "          value\n"
        '            string\t"item0"\n'
        "          value\n"
        '            string\t"item1"\n'
        "          number\t3.14\n"
        "          true\n"
    ).lstrip()
    assert parser.pretty() == expect
