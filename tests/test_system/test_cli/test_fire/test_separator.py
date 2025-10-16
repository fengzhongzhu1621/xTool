"""
$ python example.py dog cat elephant - upper
CAT DOG ELEPHANT

$ python example.py dog cat elephant upper
cat dog upper elephant

$ python example.py dog cat elephant X upper -- --separator=X
CAT DOG ELEPHANT
"""

import fire


def order_by_length(*items):
    """Orders items by length, breaking ties alphabetically."""
    sorted_items = sorted(items, key=lambda item: (len(str(item)), str(item)))
    return ' '.join(sorted_items)


if __name__ == '__main__':
    fire.Fire(order_by_length)
