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

> python test_default_param.py bob --greeting hi
hi, bob!

> python test_default_param.py bob --greeting=hi
hi, bob!

> python test_default_param.py bob -g=hi
hi, bob!

> python test_default_param.py bob -g hi
hi, bob!

"""

import fire


def greet(name, greeting='Hello'):
    return f'{greeting}, {name}!'


if __name__ == '__main__':
    fire.Fire(greet)
