#!python
# cython: language_level=3, boundscheck=False, wraparound=False

"""
**************************************************************************************
大小端
In [23]: a = 0x12345678
In [24]: hex(a)
Out[24]: '0x12345678'

In [25]: bin(a)
Out[25]: '0b10010001101000101011001111000'

In [26]: int(a)
Out[26]: 305419896

**************************************************************************************
查看系统默认大小端
In [16]: import sys

In [17]: sys.byteorder
Out[17]: 'little'

**************************************************************************************
小端序(Little-Endian)：低位字节排放在内存的低地址端即该值的起始地址，高位字节排放在内存的高地址端。
 ------------------------------------------------
｜ 0x12    |   0x34    |   0x56    |     0x78    |
 ------------------------------------------------
 地址0x0003   地址0x0002   地址0x0001   地址0x0000

**************************************************************************************
大端序(Big-Endian)：高位字节排放在内存的低地址端即该值的起始地址，低位字节排放在内存的高地址端。
 ------------------------------------------------
｜ 0x78    |   0x56    |   0x34    |     0x12    |
 ------------------------------------------------
 地址0x0003   地址0x0002   地址0x0001   地址0x0000

**************************************************************************************
在网络字节序中，使用的是大端字节序，4个字节的整数0x12345678转化为字节序内存地址如下
  ------------------------------------------------
｜ 0x78    |   0x56    |   0x34    |     0x12    |
 ------------------------------------------------
 地址0x0003   地址0x0002   地址0x0001   地址0x0000
 当接收方获得网络字节序时，需要将其转化为整型
 获得整数的第一个字节：data[3] << 0， 值为0x00000078，即 p_src[0] >> 24
 获得整数的第一个字节：data[2] << 8， 值为0x00005600，即 (p_src[0] & 0x00ff0000) >> 8
 获得整数的第一个字节：data[1] << 16，值为0x00340000，即 (p_src[0] & 0x0000ff00) << 8
 获得整数的第一个字节：data[0] << 24，值为0x12000000，即 p_src[0] << 24
 位运算 (data[3]<<0) | (data[2]<<8) | (data[1]<<16) | (data[0]<<24) 获得整数 0x12345678
 转化为本地字节序（小端）
  ------------------------------------------------
｜ 0x12    |   0x34    |   0x56    |     0x78    |
 ------------------------------------------------
 地址0x0003   地址0x0002   地址0x0001   地址0x0000
"""

from libc.string cimport strcpy
from libc.string cimport memset
from cpython.ref cimport PyObject, Py_INCREF, Py_DECREF
from cpython.bytes cimport PyBytes_FromStringAndSize


cdef void endian_byte_to_ushort(char * src, char * dest):
    cdef ushort * p_src = <ushort * > src
    cdef ushort * p_dest = <ushort * > dest
    p_dest[0] = (p_src[0] >> 8) | (p_src[0] << 8)


cdef void endian_byte_to_uint(char * src, char * dest):
    cdef uint * p_src = <uint * > src
    cdef uint * p_dest = <uint * > dest
    p_dest[0] = (
        p_src[0] >> 24) | (
        (p_src[0] & 0x00ff0000) >> 8) | (
            (p_src[0] & 0x0000ff00) << 8) | (
                p_src[0] << 24)


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
        cdef lock_guard[recursive_mutex] * lck = new lock_guard[recursive_mutex](self.enqueue_mtx)
        self.queue_a.push(value)
        del lck
        return 0

    cpdef int enqueue(self, int value):
        cdef int ret = self._enqueue(value)
        return ret

    cdef int _dequeue(self) nogil:
        cdef lock_guard[recursive_mutex] * lck = new lock_guard[recursive_mutex](self.dequeue_mtx)
        # 获得队首元素的引用
        cdef int value = self.queue_a.front()
        # 弹出队首元素
        self.queue_a.pop()
        del lck
        return value

    cpdef int dequeue(self):
        cdef int value = self._dequeue()
        return value
