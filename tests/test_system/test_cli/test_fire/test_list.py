"""
> python test_list.py --help

NAME
    test_list.py

SYNOPSIS
    test_list.py ITEMS

POSITIONAL ARGUMENTS
    ITEMS

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS

> python test_list.py abc

A
B
C


> python test_list.py 123
Traceback (most recent call last):
TypeError: 'int' object is not iterable


> python test_list.py a b c
ERROR: Unable to index into component with argument: b
Usage: test_list.py a <command|index>
  available commands:    append | clear | copy | count | extend | index |
                         insert | pop | remove | reverse | sort
  available indexes:     0

For detailed information on this command, run:
  test_list.py a --help

"""

import fire


def process_list(items):
    return [item.upper() for item in items]


if __name__ == '__main__':
    fire.Fire(process_list)
