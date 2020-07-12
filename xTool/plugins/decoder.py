# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class BaseDecoder(metaclass=ABCMeta):
    @abstractmethod
    def decode(self, config_data: bytes, options: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def set_options(self, options: dict) -> None:
        raise NotImplementedError
