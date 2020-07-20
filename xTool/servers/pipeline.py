# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class IPipelineConnector(metaclass=ABCMeta):
    @abstractmethod
    def close_other_side(self):
        raise NotImplementedError
