#!python
#cython: language_level=3, boundscheck=False, wraparound=False

import pickle


cdef class PickleCodec:
    cpdef bytes encode(self, object obj):
        return pickle.dumps(obj)

    cpdef object decode(self, bytes data):
        return pickle.loads(data)
