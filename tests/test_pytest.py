import pytest


# 定义一个 fixture 函数，提供参数 x
@pytest.fixture
def x():
    return 2


# 定义一个测试函数，接受参数 x 和 y
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (1, 2, 4),
        (2, 3, 5),
    ],
    indirect=["x"],
)
def test_addition_indirect_x(x, y, expected):
    # 当你需要将某些参数传递给测试函数，但这些参数本身是由其他 fixture 提供的时，可以使用 indirect 参数。
    # indirect 参数允许你将一个或多个参数标记为间接参数。
    # 这意味着这些参数将由相应的 fixture 函数提供，而不是直接从 parametrize 装饰器中获取。
    assert 2 + y == expected


# 定义一个测试函数，接受参数 x 和 y
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (1, 2, 3),
        (2, 3, 5),
    ],
)
def test_addition_without_indirect(x, y, expected):
    assert x + y == expected
