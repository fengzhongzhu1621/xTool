#!python
#cython: language_level=3, boundscheck=False, wraparound=False

from libc.string cimport strcpy
from libc.string cimport memset
from cpython.ref cimport PyObject,Py_INCREF,Py_DECREF
from cpython.bytes cimport PyBytes_FromStringAndSize


cdef class CythonDemo:
    def __init__(self):
        memset(self.char_a, 0, 16)

    cpdef str strcpy(self):
        str_value = "abc"
        strcpy(self.char_a, str_value.encode("utf8"))
        result = self.char_a.decode('utf8')
        return result

    cpdef uint get_queue_size(self):
        self.queue_a.push(100)
        self.queue_a.push(200)
        return self.queue_a.size()

    cdef int _enqueue(self, int value) nogil:
        cdef lock_guard[recursive_mutex]* lck = new lock_guard[recursive_mutex](self.enqueue_mtx)
        self.queue_a.push(value)
        del lck
        return 0

    cpdef int enqueue(self, int value):
        cdef int ret = self._enqueue(value)
        return ret

    cdef int _dequeue(self) nogil:
        cdef lock_guard[recursive_mutex]* lck = new lock_guard[recursive_mutex](self.dequeue_mtx)
        # 获得队首元素的引用
        cdef int value = self.queue_a.front()
        # 弹出队首元素
        self.queue_a.pop()
        del lck
        return value

    cpdef int dequeue(self):
        cdef int value = self._dequeue()
        return value
