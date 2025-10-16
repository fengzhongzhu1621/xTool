"""
链式调用

$ python test_method_chaining.py move 3 3 on move 3 6 on move 6 3 on move 6 6 on move 7 4 on move 7 5 on __str__
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 1 0 0 1 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 1 0 0 1 0 0 0
0 0 0 0 1 1 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
"""

import fire


class BinaryCanvas:
    """A canvas with which to make binary art, one bit at a time."""

    def __init__(self, size=10):
        self.pixels = [[0] * size for _ in range(size)]
        self._size = size
        self._row = 0  # The row of the cursor.
        self._col = 0  # The column of the cursor.

    def __str__(self):
        return '\n'.join(' '.join(str(pixel) for pixel in row) for row in self.pixels)

    def show(self):
        print(self)
        return self

    def move(self, row, col):
        self._row = row % self._size
        self._col = col % self._size
        return self

    def on(self):
        return self.set(1)

    def off(self):
        return self.set(0)

    def set(self, value):
        self.pixels[self._row][self._col] = value
        return self


if __name__ == '__main__':
    fire.Fire(BinaryCanvas)
