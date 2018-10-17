#coding: utf-8

"""
    Generate a sequence of items that put onto a queue
    Consume items on a queue.
"""


def sendto_queue(source, the_queue):
    """将数据发送到队列 ."""
    for item in source:
        the_queue.put(item)
    the_queue.put(StopIteration)


def genfrom_queue(the_queue):
    """从队列中循环获取数据 ."""
    while True:
        item = the_queue.get()
        if item is StopIteration:
            break
        yield item
