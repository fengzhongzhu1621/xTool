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
from libc.string cimport memset, memcpy, memmove
from cpython.ref cimport PyObject, Py_INCREF, Py_DECREF
from cpython.bytes cimport PyBytes_FromStringAndSize
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free


cdef void endian_byte_to_ushort(char * src, char * dest):
    """大端字节转换为无符号短整型 ."""
    cdef ushort * p_src = <ushort * > src
    cdef ushort * p_dest = <ushort * > dest
    p_dest[0] = (p_src[0] >> 8) | (p_src[0] << 8)


cdef void endian_byte_to_uint(char * src, char * dest):
    """大端字节转换为无符号整型 ."""
    cdef uint * p_src = <uint * > src
    cdef uint * p_dest = <uint * > dest
    p_dest[0] = (
        p_src[0] >> 24) | (
        (p_src[0] & 0x00ff0000) >> 8) | (
            (p_src[0] & 0x0000ff00) << 8) | (
                p_src[0] << 24)


# 协议帧头大小
cdef uint FRAME_HEAD_LEN = 16
# Magic
cdef ushort FRMAE_HEAD_MAGIC_VALUE = 1234


cdef class CythonDemo:
    def __init__(self):
        memset(self.char_a, 0, 16)
        self.buf = bytearray()

    def __cinit__(self):
        self.data_length = 0    # TODO 数据的真实大小，可能非常大超出int的范围
        self.buffer_size = 128
        self.buffer = self.malloc(self.buffer_size)
        if not self.buffer:
            raise MemoryError()

    cdef char * malloc(self, size_t length):
        buffer = <char * > PyMem_Malloc(length * sizeof(char))
        if not buffer:
            raise MemoryError()
        return buffer

    cpdef void resize(self, size_t length):
        new_buffer = <char*> PyMem_Realloc( < void * >self.buffer, length * sizeof(char))
        if not new_buffer:
            raise MemoryError()
        self.buffer_size = length
        self.buffer = new_buffer

    cpdef void reset(self):
        self.buf = bytearray()

    cpdef void append_buffer_data(self, bytes data):
        self.buf.extend(data)

    cdef void memcpy(self, int offset, int length):
        cdef uint i = 0
        while i < length:
            self.buffer[i] = self.buffer[offset + i]
            i += 1
        self.data_length = length

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

    cpdef void reset_buffer(self):
        self.data_length = 0

    cpdef int get_buffer_data_length(self):
        return self.data_length

    cpdef void append_buffer(self, bytes data):
        """填充buffer ."""
        # 获得需要填充的数据字节大小
        cdef int append_data_length = len(data)
        # 如果缓冲区满，则扩充缓冲区
        if self.data_length + append_data_length > self.buffer_size:
            self.resize((self.buffer_size + append_data_length) * 2)
        # 将追加的数据添加到缓冲区
        cdef char * start_ptr = self.buffer + self.data_length   # 需要追加数据的起始位置
        cdef char * from_ptr = data
        memcpy(start_ptr, from_ptr, append_data_length)
        # 记录追加后的总数据长度
        self.data_length += append_data_length

    cpdef list read_package(self):
        """读取协议包 ."""
        packages = []
        cdef int package_start_index = 0
        cdef ushort magic = 0
        cdef uint package_len = 0

        # ---------------------------------------------------------------------------
        # ｜  magic(2)  |   package_len(4)   |      |       |         data            |
        # ---------------------------------------------------------------------------
        # |           FRAME_HEAD_LEN (16)                   |

        # 判断package是否完整，是否包含完整的帧头
        while package_start_index + FRAME_HEAD_LEN <= self.data_length:
            # 判断magic是否匹配
            endian_byte_to_ushort(self.buffer + package_start_index, < char*> & magic)
            if magic != FRMAE_HEAD_MAGIC_VALUE:
                raise Exception("framer head magic not match")
            # 判断包长度是否匹配，包长度必须大于帧头的长度
            endian_byte_to_uint(self.buffer + package_start_index + 2, < char*> & package_len)
            if package_len <= FRAME_HEAD_LEN:
                raise Exception("frame header length not match")
            # 提取包
            if package_start_index + package_len > self.data_length:
                # 包缺失部分数据，则停止遍历，删除已经遍历的包
                if package_start_index > 0:
                    self.memcpy(
                        package_start_index,
                        self.data_length -
                        package_start_index)
                    self.data_length -= package_start_index
                return packages
            else:
                # 如果遍历到一个完整的包，则记录包
                packages.append(
                    bytes(self.buffer[package_start_index:package_start_index + package_len]))
                # 记录下一个包的起始位置
                package_start_index += package_len

        ########################################################################################
        #            package_start_index   self.data_length
        #                ||                   ||
        #                \/                   \/
        #  ------------------------------------------
        # ｜              |  FRAME_HEAD_LEN (16)     |
        #  ------------------------------------------
        ########################################################################################

        # 删除已经遍历的包
        if package_start_index > 0 and self.data_length - package_start_index > 0:
            self.memcpy(
                package_start_index,
                self.data_length -
                package_start_index)
            self.data_length -= package_start_index

        return packages

    def __dealloc__(self):
        PyMem_Free(< void*>self.buffer)
