from lark import Transformer, Tree, v_args


def test_vargs():
    @v_args()
    class MyTransformer(Transformer):
        @staticmethod
        def integer(*args, **kwargs):
            return args, kwargs

        @classmethod
        def integer2(cls, *args, **kwargs):
            return args, kwargs

        hello = staticmethod(lambda args: "hello")

    x = MyTransformer().transform(Tree("integer", [2]))
    assert x == (([2],), {})
    x = MyTransformer().transform(Tree("integer2", [2]))
    assert x == (([2],), {})
    x = MyTransformer().transform(Tree("hello", [2]))
    assert x == "hello"


def test_vargs_inline():
    @v_args(inline=True)
    class MyTransformer(Transformer):
        @staticmethod
        def integer(*args, **kwargs):
            return args, kwargs

        @classmethod
        def integer2(cls, *args, **kwargs):
            return args, kwargs

        def integer3(self, *args, **kwargs):
            return args, kwargs

        hello = staticmethod(lambda args: "hello")

    x = MyTransformer().transform(Tree("integer", [2]))
    assert x == ((2,), {})
    x = MyTransformer().transform(Tree("integer2", [2]))
    assert x == ((2,), {})
    x = MyTransformer().transform(Tree("integer3", [2]))
    assert x == ((2,), {})
    x = MyTransformer().transform(Tree("hello", [2]))
    assert x == "hello"


def test_vargs_tree():
    @v_args(tree=True)
    class MyTransformer(Transformer):
        @staticmethod
        def integer(*args, **kwargs):
            return args, kwargs

        @classmethod
        def integer2(cls, *args, **kwargs):
            return args, kwargs

        def integer3(self, *args, **kwargs):
            return args, kwargs

        hello = staticmethod(lambda args: "hello")

    x = MyTransformer().transform(Tree("integer", [2]))
    assert x == ((Tree("integer", [2]),), {})
    x = MyTransformer().transform(Tree("integer2", [2]))
    assert x == ((Tree("integer2", [2]),), {})
    x = MyTransformer().transform(Tree("integer3", [2]))
    assert x == ((Tree("integer3", [2]),), {})
    x = MyTransformer().transform(Tree("hello", [2]))
    assert x == "hello"


def test_transformer():
    t = Tree(
        "add",
        [
            Tree(
                "sub",
                [
                    Tree("i", ["3"]),
                    Tree("f", ["1.1"]),
                ],
            ),
            Tree("i", ["1"]),
        ],
    )

    class T(Transformer):
        i = v_args(inline=True)(int)
        f = v_args(inline=True)(float)

        def sub(self, values):
            return values[0] - values[1]

        def add(self, values):
            return values[0] + values[1]

    assert T().transform(t) == 2.9

    class T1(Transformer):
        i = v_args(inline=True)(int)
        f = v_args(inline=True)(float)

        @v_args(inline=True)
        def sub(self, a, b):
            return a - b

        @v_args(inline=True)
        def add(self, a, b):
            return a + b

    assert T1().transform(t) == 2.9
