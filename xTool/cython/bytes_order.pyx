#!python
# cython: language_level=3, boundscheck=False, wraparound=False

"""
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
"""

from libc.stdint cimport uint8_t, uint16_t, uint32_t


cpdef bytes endian_uchar_to_bytes(uint8_t i):
    return ( < char * >&i)[:sizeof(uint8_t)]


cpdef bytes endian_ushort_to_bytes(uint16_t i):
    i = (i >> 8) | (i << 8)
    return ( < char * >&i)[:sizeof(uint16_t)]


cpdef bytes endian_uint_to_bytes(uint32_t i):
    i = (
        i >> 24) | (
        (i >> 8) & 0x0000FF00) | (
            (i << 8) & 0x00FF0000) | (
                i << 24)
    return ( < char * >&i)[:sizeof(uint32_t)]
