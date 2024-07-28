"""
> python test_default_param.py -h

NAME
    test_default_param.py

SYNOPSIS
    test_default_param.py NAME <flags>

POSITIONAL ARGUMENTS
    NAME

FLAGS
    -g, --greeting=GREETING
        Default: 'Hello'

$ python test_default_param.py bob --greeting hi
hi, bob!

$ python test_default_param.py bob --greeting=hi
hi, bob!

$ python test_default_param.py bob -g=hi
hi, bob!

$ python test_default_param.py bob -g hi
hi, bob!

$ python test_default_param.py add 10 20
31
$ python test_default_param.py multiply 10 20
201

$ python test_default_param.py add 10 20 --offset=0
30
$ python test_default_param.py multiply 10 20 --offset=0
200

# 连字符和下划线（ -和_）在成员名称和标志名称中是可以互换的。
# 构造函数的参数可以在其他函数的参数之后或函数之前
# 标志名称和其值之间的等号是可选的
$ python test_default_param.py --name="Sherrerd Hall" --stories=3 climb_stairs 10
$ python test_default_param.py --name="Sherrerd Hall" climb_stairs --stairs_per_story=10
$ python test_default_param.py --name="Sherrerd Hall" climb_stairs --stairs-per-story 10
$ python test_default_param.py climb-stairs --stairs-per-story 10 --name="Sherrerd Hall"
"""

import fire


def greet(name, greeting='Hello'):
    return f'{greeting}, {name}!'


class BrokenCalculator:

    def __init__(self, offset=1):
        self._offset = offset

    def add(self, x, y):
        return x + y + self._offset

    def multiply(self, x, y):
        return x * y + self._offset


class Building:

    def __init__(self, name, stories=1):
        self.name = name
        self.stories = 1

    def climb_stairs(self, stairs_per_story=10):
        for story in range(self.stories):
            for stair in range(1, stairs_per_story):
                yield stair
                yield 'Phew!'
        yield 'Done!'


if __name__ == '__main__':
    fire.Fire(greet)
    # fire.Fire(BrokenCalculator)
    # fire.Fire(Building)
