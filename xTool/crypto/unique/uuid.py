import uuid
from typing import Set


def uniqid():
    return uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex


def uniqid4():
    return str(uuid.uuid4())


def unique_id(prefix: str) -> str:
    """支持前缀的 uuid4 ."""
    if len(prefix) != 1:
        raise ValueError("prefix length must be 1")

    return "{}{}".format(prefix, uuid.uuid4().hex)


def generate_root_id():
    return uuid.uuid1().hex[:14]


class SequenceManager:
    """全局唯一ID生成器 ."""

    def __init__(self, cache: object, key: str = "unique_sequence", pool_size: int = 3):
        self.cache = cache
        self.key = key
        self.pool: Set = set()
        # 缓存池的容量
        self.pool_size = pool_size

    def _preload_pool(self) -> None:
        poll_size = len(self.pool)
        if poll_size >= self.pool_size:
            # 缓冲池已满
            return
        # 缓冲未满，获得缓存池剩余的容量
        fetch_size = self.pool_size - poll_size
        # 生成多个序号，减少 IO 消耗
        max_seq = self.cache.incrby(self.key, fetch_size)
        min_seq = max_seq - fetch_size
        # 将新生成的序列放到缓冲区
        self.pool.update(range(max_seq, min_seq, -1))

    def generate(self) -> int:
        """创建唯一 ID ."""
        if not self.pool:
            # 预先生成多个序号并缓存
            self._preload_pool()
        # 从缓存池获取一个唯一 ID
        sequence = self.pool.pop()
        return sequence

    def clear_pool(self) -> None:
        self.pool.clear()
