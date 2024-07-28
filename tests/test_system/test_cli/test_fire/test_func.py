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

$ python test_func.py world
Hello, world!

$ python test_func.py --name=world
Hello, world!

$ python test_func.py dog cat elephant - upper
CAT DOG ELEPHANT

$ python test_func.py dog cat elephant upper
cat dog upper elephant
"""

import fire


def greet(name):
    return f'Hello, {name}!'


def order_by_length(*items):
    """Orders items by length, breaking ties alphabetically."""
    sorted_items = sorted(items, key=lambda item: (len(str(item)), str(item)))
    return ' '.join(sorted_items)


if __name__ == '__main__':
    fire.Fire(greet)
    # fire.Fire(order_by_length)
