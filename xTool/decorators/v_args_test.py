from xTool.decorators import Decoratable, apply_visit_wrapper, v_args


class Transformer(Decoratable):
    @v_args(inline=True)
    def mul(self, left: int, right: int) -> int:
        return left * right


def test__vargs_inline():
    transformer = Transformer()
    user_callback_name = "mul"
    f = getattr(transformer, user_callback_name)
    # 获得函数的自定义装饰器
    wrapper = getattr(f, "visit_wrapper", None)
    # 函数执行前，先执行自定义装饰器
    f = apply_visit_wrapper(f, user_callback_name, wrapper)
    # 函数执行前，修改类参数的格式
    actual = f(*([2, 3],), **{})
    expect = 6
    assert actual == expect
