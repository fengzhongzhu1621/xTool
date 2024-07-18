"""
> python test_class.py -- --help

NAME
    test_class.py

SYNOPSIS
    test_class.py -
(END)

> python test_class.py add --help

NAME
    test_class.py add

SYNOPSIS
    test_class.py add A B

POSITIONAL ARGUMENTS
    A
    B

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS

"""

import fire


class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b


if __name__ == '__main__':
    fire.Fire(Calculator)
