# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

import six


class BaseDataBackend(six.with_metaclass(ABCMeta, object)):
    @abstractmethod
    def exists(self, key):
        return NotImplementedError()

    @abstractmethod
    def incr_expireat(self, name, amount, when):
        return NotImplementedError()
