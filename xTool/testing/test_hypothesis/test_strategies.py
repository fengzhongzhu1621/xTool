from typing import List

import hypothesis.strategies as st
from hypothesis import assume, example, given, settings
from jsondiff import diff

from xTool.testing.random import generate_random_json, perturbate_json


def generate_scenario_no_sets(rng):
    a = generate_random_json(rng, sets=False)
    b = perturbate_json(a, rng, sets=False)
    return a, b


def non_negative_integers():
    return st.integers(min_value=0)


def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


# 策略是用于生成输入数据的对象。
# Hypothesis 提供了各种内置策略，例如 st.integers() 用于生成整数、st.text() 用于生成文本等。
# 还可以自定义策略以生成特定类型的数据。
@given(st.integers(), st.integers())
def test_divide(a: int, b: int):
    # 假设来限定输入数据的范围或属性。
    # 如果假设不满足，Hypothesis 将自动生成不合规范的输入数据并进行测试。
    # 假设通常用 assume() 函数来声明。
    assume(b != 0)
    result = divide(a, b)
    assert result == a / b


# 生成整数列表作为输入数据
@given(st.lists(st.integers()))
def test_sorted_list(arr: List[int]):
    sorted_arr = sorted(arr)
    for i in range(len(sorted_arr) - 1):
        assert sorted_arr[i] <= sorted_arr[i + 1]


@given(x=st.integers(), y=st.integers())
@example(x=1, y=2)
def test_example(x, y):
    assert x + y == y + x


@given(s=st.text(), l=st.lists(st.text()))
def test_string_concatenation(s, l):
    result = s + "".join(l)
    assert len(result) == len(s) + sum(len(x) for x in l)


@given(x=non_negative_integers())
def test_positive_addition(x):
    assert x + 1 > x


@given(st.randoms().map(generate_scenario_no_sets))
@settings(max_examples=10)
def test_dump(scenario):
    a, b = scenario
    diff(a, b, syntax="compact", dump=True)
