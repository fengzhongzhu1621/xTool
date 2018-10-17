#coding: utf-8

from xTool.decorators.decorators import *


def test_timethis():
    @timethis
    def funA():
        pass

    with timethis("hello world!"):
        funA()
