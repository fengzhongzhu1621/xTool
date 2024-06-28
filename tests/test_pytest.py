import pytest


@pytest.fixture
def x():
    return 2


@pytest.fixture
def y():
    return 3


@pytest.fixture
def expected():
    return 5


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


@pytest.mark.parametrize(
    "x, y, expected",
    [
        (1, 2, 3),
        (2, 3, 5),
    ],
)
def test_addition_without_indirect(x, y, expected):
    assert x + y == expected


@pytest.fixture
def y():
    return 3


@pytest.mark.parametrize(
    "x, y, expected",
    [
        (1, 2, 6),
        (2, 3, 6),
    ],
    indirect=True,
)
def test_addition_indirect_is_true(x, y, expected):
    assert x + y == expected
