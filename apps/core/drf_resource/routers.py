# -*- coding: utf-8 -*-

from dataclasses import dataclass

from .base import Resource


@dataclass
class ResourceRoute:
    method: str
    resource_class: Resource
    endpoint: str

    def __post_init__(self):
        self.method = self.method.lower()
