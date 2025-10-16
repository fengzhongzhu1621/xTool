"""
使用cycler避免了多重循环
"""

from collections import defaultdict

import pytest
from cycler import concat, cycler


def test_cycler_factory():
    # cycler(*args, **kwargs)：工厂函数，创建一个Cycler对象
    # cycler(arg)：arg为Cycler对象。复制Cycler对象的构造函数。
    # cycler(label1=iter1[, label2=iter2[, ...]])：label必须是有效的Python标识符，要求类似字典的键，iter为可迭代对象。求多组参数的点积，功能类似于zip()函数。
    # cycler(label, itr)：从一对label和可迭代对象构造Cycler对象。这里label可以为整数和带空格的字符串。
    #
    # cycler对象是一个迭代器，迭代输出的对象为字典结构，键为关键字参数名称，值为序列的元素。
    color_cycle = cycler(color=["r", "g", "b"])
    assert len(color_cycle) == 3
    for color in color_cycle:
        print(color)
    # {'color': 'r'}
    # {'color': 'g'}
    # {'color': 'b'}

    for color in cycler(ec=color_cycle):
        print(color)
    # {'color': 'r'}
    # {'color': 'g'}
    # {'color': 'b'}

    cyl = cycler("c", "rgb") + cycler("lw", range(1, 4))
    assert cyl.by_key() == {"c": ["r", "g", "b"], "lw": [1, 2, 3]}


def test_keys():
    color_cycle = cycler(color=["r", "g", "b"])
    assert color_cycle.keys == {"color"}


def test_add():
    color_cycle = cycler(color=["r", "g", "b"])
    lw_cycle = cycler(lw=range(1, 4))
    wc = lw_cycle + color_cycle
    assert wc.keys == {"color", "lw"}

    for s in wc:
        print(s)
    # {'lw': 1, 'color': 'r'}
    # {'lw': 2, 'color': 'g'}
    # {'lw': 3, 'color': 'b'}

    wc = cycler(color=["r", "g", "b"], lw=range(3))
    for s in wc:
        print(s)
    # {'color': 'r', 'lw': 0}
    # {'color': 'g', 'lw': 1}
    # {'color': 'b', 'lw': 2}


def test_product():
    color_cycle = cycler(color=["r", "g", "b"])
    lw_cycle = cycler(lw=range(1, 4))
    # 求两个对象的元素的笛卡尔积，功能类似于Python内置的itertools.product()函数。
    wc = lw_cycle * color_cycle
    for s in wc:
        print(s)
    # {'lw': 1, 'color': 'r'}
    # {'lw': 1, 'color': 'g'}
    # {'lw': 1, 'color': 'b'}
    # {'lw': 2, 'color': 'r'}
    # {'lw': 2, 'color': 'g'}
    # {'lw': 2, 'color': 'b'}
    # {'lw': 3, 'color': 'r'}
    # {'lw': 3, 'color': 'g'}
    # {'lw': 3, 'color': 'b'}

    # 遍历n次cycler对象
    for s in color_cycle * 2:
        print(s)
    # {'color': 'r'}
    # {'color': 'g'}
    # {'color': 'b'}
    # {'color': 'r'}
    # {'color': 'g'}
    # {'color': 'b'}


def test_concat():
    # concat(left, right) ：拼接两个cycler对象。 前提就是两个对象必须有相同的键.
    color_cycle = cycler(color=["r", "g", "b"])
    color_cycle2 = cycler(color=["c", "m", "y", "k"])
    color_cycle = color_cycle.concat(color_cycle2)
    for s in color_cycle:
        print(s)
    # {'color': 'r'}
    # {'color': 'g'}
    # {'color': 'b'}
    # {'color': 'c'}
    # {'color': 'm'}
    # {'color': 'y'}
    # {'color': 'k'}

    color_cycle = cycler(color=["r", "g", "b"])
    for s in concat(color_cycle, color_cycle):
        print(s)
    # {'color': 'r'}
    # {'color': 'g'}
    # {'color': 'b'}
    # {'color': 'r'}
    # {'color': 'g'}
    # {'color': 'b'}


def test_slice():
    color_cycle = cycler(color=["r", "g", "b"])
    for s in color_cycle[:2]:
        print(s)
    # {'color': 'r'}
    # {'color': 'g'}

    for s in color_cycle[::-1]:
        print(s)
    # {'color': 'b'}
    # {'color': 'g'}
    # {'color': 'r'}


def test_zip():
    color_cycle = cycler(color=["r", "g", "b"])
    for j, c in zip(range(5), color_cycle):
        print(j, c)
    # 0 {'color': 'r'}
    # 1 {'color': 'g'}
    # 2 {'color': 'b'}

    cc = color_cycle()
    for j, c in zip(range(5), cc):
        print(j, c)
    # 0 {'color': 'r'}
    # 1 {'color': 'g'}
    # 2 {'color': 'b'}
    # 3 {'color': 'r'}
    # 4 {'color': 'g'}


def test_by_key():
    color_cycle = cycler(color=["r", "g", "b"])
    bk = color_cycle.by_key()
    assert bk == {"color": ["r", "g", "b"]}

    bk["color"] = ["green"] * len(color_cycle)
    assert cycler(**bk).by_key() == {"color": ["green", "green", "green"]}


def test_finite():
    color_cycle = cycler("c", "rgb")
    finite_cy_iter = iter(color_cycle)
    dd_finite = defaultdict(lambda: next(finite_cy_iter))
    assert dd_finite["a"] == {"c": "r"}
    assert dd_finite["b"] == {"c": "g"}
    assert dd_finite["c"] == {"c": "b"}
    with pytest.raises(StopIteration):
        dd_finite["d"]


def test_repeating():
    color_cycle = cycler("c", "rgb")
    finite_cy_iter = color_cycle()
    dd_finite = defaultdict(lambda: next(finite_cy_iter))
    assert dd_finite["a"] == {"c": "r"}
    assert dd_finite["b"] == {"c": "g"}
    assert dd_finite["c"] == {"c": "b"}
    assert dd_finite["d"] == {"c": "r"}
