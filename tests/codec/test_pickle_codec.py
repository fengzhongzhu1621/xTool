# -*- coding: utf-8 -*-

import pickle
from timeit import Timer
from xTool.codec.pickle_codec import PickleCodec


class PyPickleCodec:
    def encode(self, obj):
        return pickle.dumps(obj)

    def decode(self, data):
        return pickle.loads(data)


py_codec = PyPickleCodec()
cython_codec = PickleCodec()


@Timer
def benchmark_py_picke_codec():
    value = py_codec.encode({"a": 1, "b": 2})
    py_codec.decode(value)


@Timer
def benchmark_cython_picke_codec():
    value = cython_codec.encode({"a": 1, "b": 2})
    cython_codec.decode(value)


print("benchmark_py_picke_codec: ", benchmark_py_picke_codec.timeit())
print("benchmark_cython_picke_codec: ", benchmark_cython_picke_codec.timeit())
