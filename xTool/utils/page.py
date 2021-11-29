# -*- coding: utf-8 -*-

from typing import Dict


class Page:
    def __init__(self, limit, offset):
        self.limit = limit  # 每页的数量
        self.offset = offset  # 数据偏移量

    @property
    def slice_from(self):
        return self.offset

    @property
    def slice_to(self):
        if self.limit == 0:
            return None
        return self.offset + self.limit


def get_page_obj(page_data: Dict):
    """构造Page对象 ."""
    return Page(limit=page_data.get("limit", 0), offset=page_data.get("offset", 0))
