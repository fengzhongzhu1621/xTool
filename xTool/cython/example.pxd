#!python
# cython: language_level=3, boundscheck=False, wraparound=False

cdef class CythonDemo:
    cdef:
        public object object_a
        int int_a
        char char_a[16]
        bint b_int_a

    cpdef str action_strcpy(self)
