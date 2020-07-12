# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import List


class ServcieMethod:
    """服务的一个接口方法 ."""
    def __init__(self, name):
        self.name = name


class ServiceDesc:
    def __init__(self, service_name: str, methods: List[ServcieMethod]):
        # 服务名
        self.service_name = service_name
        # 服务的所有接口方法
        self.methods = methods


class BaseService(metaclass=ABCMeta):
    @abstractmethod
    def register(self, service_desc: ServiceDesc):
        raise NotImplementedError

    @abstractmethod
    def run(self):
        raise NotImplementedError


class Service(BaseService):
    def register(self, service_desc: ServiceDesc):
        pass

    @abstractmethod
    def run(self):
        pass
