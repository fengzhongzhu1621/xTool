import pickle

import pytest


class PyPickleCodec:
    def encode(self, obj):
        return pickle.dumps(obj)

    def decode(self, data):
        return pickle.loads(data)


py_codec = PyPickleCodec()


@pytest.mark.skip
# @Timer
def test_benchmark_py_picke_codec():
    value = {"a": 1, "b": 2}
    value_codec = py_codec.encode(value)
    actual = py_codec.decode(value_codec)
    assert actual == value


@pytest.mark.skip
# @Timer
def test_benchmark_cython_picke_codec():
    from xTool.crypto.codec.pickle_codec_c import PickleCodec

    cython_codec = PickleCodec()
    value = {"a": 1, "b": 2}
    value_codec = cython_codec.encode(value)
    actual = cython_codec.decode(value_codec)
    assert actual == value


# print("benchmark_py_picke_codec: ", Timer(test_benchmark_py_picke_codec).timeit())
# print("benchmark_cython_picke_codec: ", Timer(test_benchmark_cython_picke_codec).timeit())
