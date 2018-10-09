#coding: utf-8

"""
    Generate a sequence of items that put onto a queue
    Consume items on a queue.
"""


def sendto_queue(source, the_queue):
    for item in source:
        the_queue.put(item)
    the_queue.put(StopIteration)


def genfrom_queue(the_queue):
    while True:
        item = the_queue.get()
        if item is StopIteration:
            break
        yield item
