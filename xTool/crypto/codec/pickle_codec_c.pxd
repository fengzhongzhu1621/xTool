#!python
#cython: language_level=3, boundscheck=False, wraparound=False


cdef class PickleCodec:
    cpdef bytes encode(self, object obj)
    cpdef object decode(self, bytes data)
