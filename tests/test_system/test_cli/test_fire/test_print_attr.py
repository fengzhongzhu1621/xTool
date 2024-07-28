"""
$ python test_print_attr.py --code=A name
airport

$ python test_print_attr.py --code=B name
body

$ python test_print_attr.py --code=B name upper
BODY
"""

import fire

MAP = {"A": "airport", "B": "body", "C": "circle"}


class Airport:

    def __init__(self, code):
        self.code = code
        self.name = MAP.get(self.code)


if __name__ == '__main__':
    fire.Fire(Airport)
