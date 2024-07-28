r"""
$ python test_type_convert.py 10
int
$ python test_type_convert.py 10.0
float
$ python test_type_convert.py hello
str
$ python test_type_convert.py '(1,2)'
tuple
$ python test_type_convert.py [1,2]
list
$ python test_type_convert.py True
bool
$ python test_type_convert.py {name: David}
dict


$ python test_type_convert.py 10
int
$ python test_type_convert.py "10"
int
$ python test_type_convert.py '"10"'
str
$ python test_type_convert.py "'10'"
str
$ python test_type_convert.py \"10\"
str

$ python test_type_convert.py '{"name": "David Bieber"}'  # Good! Do this.
dict
$ python test_type_convert.py {"name":'"David Bieber"'}  # Okay.
dict
$ python test_type_convert.py {"name":"David Bieber"}  # Wrong. This is parsed as a string.
str
$ python test_type_convert.py {"name": "David Bieber"}  # Wrong. This isn't even treated as a single argument.
<error>

$ python test_type_convert.py --obj=True
bool
$ python test_type_convert.py --obj=False
bool
$ python test_type_convert.py --obj
bool
$ python test_type_convert.py --noobj
bool
"""

import fire


def order_by_length(*items):
    """Orders items by length, breaking ties alphabetically."""
    sorted_items = sorted(items, key=lambda item: (len(str(item)), str(item)))
    return ' '.join(sorted_items)


if __name__ == '__main__':
    fire.Fire(lambda obj: type(obj).__name__)
