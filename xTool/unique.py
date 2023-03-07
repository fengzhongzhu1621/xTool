# -*- coding: utf-8 -*-
import uuid
from typing import Set


def uniqid():
    return uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex


def uniqid4():
    return str(uuid.uuid4())


def unique_id(prefix: str) -> str:
    if len(prefix) != 1:
        raise ValueError("prefix length must be 1")

    return "{}{}".format(prefix, uuid.uuid4().hex)


class SequenceManager:
    """全局唯一ID生成器 ."""

    def __init__(self, cache: object, key: str = "unique_sequence", pool_size: int = 3):
        self.cache = cache
        self.key = key
        self.pool: Set = set()
        self.pool_size = pool_size

    def _preload_pool(self) -> None:
        poll_size = len(self.pool)
        if poll_size >= self.pool_size:
            # 缓冲池未满
            return
        # 缓冲已满
        fetch_size = self.pool_size - poll_size
        max_seq = self.cache.incrby(self.key, fetch_size)
        min_seq = max_seq - fetch_size
        # 将新生成的序列放到缓冲区
        self.pool.update(range(max_seq, min_seq, -1))

    def generate(self) -> int:
        if not self.pool:
            self._preload_pool()
        sequence = self.pool.pop()
        return sequence

    def clear_pool(self) -> None:
        self.pool.clear()
