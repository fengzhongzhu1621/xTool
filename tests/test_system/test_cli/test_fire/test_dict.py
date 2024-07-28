"""
> python test_dict.py --help

NAME
    test_dict.py

SYNOPSIS
    test_dict.py COMMAND

COMMANDS
    COMMAND is one of the following:

     add

     multiply

> python test_dict.py add --help

NAME
    test_dict.py add

SYNOPSIS
    test_dict.py add A B

POSITIONAL ARGUMENTS
    A
    B

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS

> python test_dict.py xxx
ERROR: Cannot find key: xxx
Usage: test_dict.py <command>
  available commands:    add | multiply

For detailed information on this command, run:
  test_dict.py --help

"""

import fire


def add(x, y):
    return x + y


def multiply(x, y):
    return x * y


operations = {
    'add': lambda a, b: a + b,
    'multiply': lambda a, b: a * b,
}

if __name__ == '__main__':
    fire.Fire(operations)

    # fire.Fire(
    #     {
    #         'add': add,
    #         'multiply': multiply,
    #     }
    # )
