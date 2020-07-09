# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Callable
from asyncio import AbstractEventLoop


class BaseDataProvider(metaclass=ABCMeta):
    """数据源提供者 。"""
    @abstractmethod
    def load(self, file_path: str, options: dict) -> bytes:
        """加载配置数据 ."""
        raise NotImplementedError

    @abstractmethod
    def watch(self, callback: Callable, interval: int,
              event_loop: AbstractEventLoop = None) -> None:
        """监听配置数据是否有变化 ."""
        raise NotImplementedError

    @abstractmethod
    def set_options(self, options: dict) -> None:
        """更新配置数据 ."""
        raise NotImplementedError
