#!python
#cython: language_level=3, boundscheck=False, wraparound=False

from libc.string cimport strcpy
from libc.string cimport memset
from cpython.ref cimport PyObject,Py_INCREF,Py_DECREF


cdef class CythonDemo:
    def __init__(self):
        memset(self.char_a, 0, 16)

    cpdef str action_strcpy(self):
        str_value = "abc"
        strcpy(self.char_a, str_value.encode("utf8"))
        result = self.char_a.decode('utf8')
        return result
