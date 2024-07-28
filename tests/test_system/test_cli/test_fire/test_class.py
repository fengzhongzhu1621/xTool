"""
$ python test_class.py -- --help

NAME
    test_class.py

SYNOPSIS
    test_class.py -
(END)

$ python test_class.py add --help

NAME
    test_class.py add

SYNOPSIS
    test_class.py add A B

POSITIONAL ARGUMENTS
    A
    B

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS

$ python test_class.py add 1 2
3

$ python test_class.py add --a=1 2
3

$ python test_class.py add --a=1 --b=2
3

$ python test_class.py add 10 20
31
$ python test_class.py multiply 10 20
201
$ python test_class.py add 10 20 --offset=0
30
$ python test_class.py multiply 10 20 --offset=0
200

"""

import fire


class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b


class BrokenCalculator:

    def __init__(self, offset=1):
        self._offset = offset

    def add(self, x, y):
        return x + y + self._offset

    def multiply(self, x, y):
        return x * y + self._offset


if __name__ == '__main__':
    fire.Fire(Calculator)
    # fire.Fire(BrokenCalculator)
