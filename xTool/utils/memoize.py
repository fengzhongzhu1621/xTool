#!/usr/bin/env python
# -*- coding: utf-8 -*-
# version : $Id: memoize.py 325 2018-09-07 07:15:10Z luciferliu $

"""
    缓存装饰器
"""

import time
from time import mktime
import datetime
import hashlib
import cPickle as pickle
from itertools import chain
from threading import Lock

cache = {}


def is_obsolete(entry, duration):
    """ 判断是否过期
        @entry: 缓存内容
        @duration:过期时间，精确到秒
    """
    return time.time() - entry['time'] > duration


def is_obsolete_by_day(entry):
    """ 判断是否当天过期
        @entry: 缓存内容
    """
    return mktime(datetime.date.today().timetuple()) - entry['time']


def compute_key(function, args, kw):
    """ 计算缓存key """
    if len(args) > 0 and args[0]:
        try:
            args[0].__module__
            className = getattr(args[0], '__class__')
            className = getattr(className, '__name__')
            args = tuple([className] + list(args[1:]))
        except AttributeError:
            pass
    key = pickle.dumps((function.func_name, args, kw))
    return key


def memoize(duration = 10):
    """ 缓存装饰器 """
    def _memoize(function):
        def __memoize(*args, **kw):
            # 计算key
            key = compute_key(function, args, kw)
            # 根据过期情况，从cache获取值
            if (key in cache and not is_obsolete(cache[key], duration)):
                return cache[key]['value']
            # 执行函数
            result = function(*args, **kw)
            # 缓存内容
            cache[key] = {'value': result, 'time': time.time()}
            return result

        return __memoize
    return _memoize


def memoize_by_day(function):
    """ 缓存装饰器，判断是否当天过期 """
    def _memoize(*args, **kw):
        # 计算key
        key = compute_key(function, args, kw)
        # 根据过期情况，从cache获取值
        if (key in cache and not is_obsolete_by_day(cache[key])):
            return cache[key]['value']
        # 执行函数
        result = function(*args, **kw)
        # 缓存内容
        cache[key] = {'value': result, 'time': mktime(datetime.date.today().timetuple())}
        return result
    return _memoize


def memoize_args(f):
    """
    A decorator that memoizes a function result based on its parameters. For example, this can be
    used in place of lazy initialization. If the decorating function is invoked by multiple
    threads, the decorated function may be called more than once with the same arguments.
    """

    # TODO: Recommend that f's arguments be immutable

    memory = { }

    @wraps( f )
    def new_f( *args ):
        try:
            return memory[ args ]
        except KeyError:
            r = f( *args )
            memory[ args ] = r
            return r

    return new_f


def sync_memoize_args( f ):
    """
    Like memoize, but guarantees that decorated function is only called once, even when multiple
    threads are calling the decorating function with multiple parameters.
    """

    # TODO: Think about an f that is recursive

    memory = { }
    lock = Lock( )

    @wraps( f )
    def new_f( *args ):
        try:
            return memory[ args ]
        except KeyError:
            # on cache misses, retry with lock held
            with lock:
                try:
                    return memory[ args ]
                except KeyError:
                    r = f( *args )
                    memory[ args ] = r
                    return r

    return new_f


if __name__ == '__main__':

    @memoize(duration=10)
    def testMemoize(i):
        return i+1

    @memoize_by_day
    def testMemoizeByDay(i):
        return i+1

    class TestMeoize(object):
        @memoize_by_day
        def getCeshihao(self):
            """
                预处理测试号，获得所有的测试号列表
            """
            self._ceshihao = [1,2,3]
            return self._ceshihao

        def compare(self):
            print(self.getCeshihao())

        @memoize_by_day
        def getTables(self):
            """
                获得差异日志表
            """
            self._beTables = ['20140806_65701', '20140806_74707', '20140806_75701', '20140806_80007', '20140806_80009', '20140806_80021', '20140806_80033', '20140806_80034', '20140806_9052', '20140806_9063']
            self._feTables = self._beTables
            #self._feTables = self._feDbDataRecord.getTables(self._beginTime)
            return self._beTables



    def test1():
        testMemoize(1)
        testMemoize(1)
        time.sleep(10)
        testMemoize(1)
    #test1()

    def test2():
        testMemoizeByDay(1)
        #testMemoizeByDay(1)
        #time.sleep(1)
        #testMemoizeByDay(1)
    #test2()

    def test3():
        testMeoize = TestMeoize()
        testMeoize.compare()
        testMeoize.compare()
        time.sleep(1)
        testMeoize.compare()
        print(testMeoize.getCeshihao())
    #test3()

    def test4():
        print("cache = ", cache)
        testMeoize = TestMeoize()
        print(testMeoize.getCeshihao())
        print("cache = ", cache)
        print(testMeoize.getTables())
        print("cache = ", cache)
    test4()

