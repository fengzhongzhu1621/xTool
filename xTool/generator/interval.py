from abc import ABCMeta


class AbstractIntervalGenerator(metaclass=ABCMeta):
    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1


class DefaultIntervalGenerator(AbstractIntervalGenerator):
    def next(self):
        super().next()
        return self.count ** 2


class SquareIntervalGenerator(AbstractIntervalGenerator):
    def next(self):
        super().next()
        return self.count ** 2


class NullIntervalGenerator(AbstractIntervalGenerator):
    pass


class LinearIntervalGenerator(AbstractIntervalGenerator):
    pass


class StaticIntervalGenerator(AbstractIntervalGenerator):
    """带有时间间隔的计数迭代器 ."""

    def __init__(self, interval):
        super().__init__()
        self.interval = interval

    def next(self):
        super().next()
        return self.interval
