"""
> python test_func.py -h

NAME
    test_func.py

SYNOPSIS
    test_func.py NAME

POSITIONAL ARGUMENTS
    NAME

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS

> python test_func.py world
Hello, world!

"""

import fire


def greet(name):
    return f'Hello, {name}!'


if __name__ == '__main__':
    fire.Fire(greet)
