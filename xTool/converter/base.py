# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class Converter(metaclass=ABCMeta):
    def __init__(self, key_mapping=None):
        self.key_mapping = key_mapping

    @abstractmethod
    def _eq(self, left, right):
        pass

    @abstractmethod
    def _not_eq(self, left, right):
        pass

    @abstractmethod
    def _in(self, left, right):
        pass

    @abstractmethod
    def _not_in(self, left, right):
        pass

    @abstractmethod
    def _contains(self, left, right):
        pass

    @abstractmethod
    def _not_contains(self, left, right):
        pass

    @abstractmethod
    def _starts_with(self, left, right):
        pass

    @abstractmethod
    def _not_starts_with(self, left, right):
        pass

    @abstractmethod
    def _ends_with(self, left, right):
        pass

    @abstractmethod
    def _not_ends_with(self, left, right):
        pass

    @abstractmethod
    def _lt(self, left, right):
        pass

    @abstractmethod
    def _lte(self, left, right):
        pass

    @abstractmethod
    def _gt(self, left, right):
        pass

    @abstractmethod
    def _gte(self, left, right):
        pass

    @abstractmethod
    def _any(self, left, right):
        pass

    @abstractmethod
    def _and(self, content):
        pass

    @abstractmethod
    def _or(self, content):
        pass

    @abstractmethod
    def convert(self, data):
        pass
