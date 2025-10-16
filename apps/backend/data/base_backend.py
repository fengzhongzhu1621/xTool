from abc import ABCMeta, abstractmethod

import six


class BaseDataBackend(metaclass=ABCMeta):
    @abstractmethod
    def exists(self, key):
        return NotImplementedError()

    @abstractmethod
    def incr_expireat(self, name, amount, when):
        return NotImplementedError()
