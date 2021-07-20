# -*- coding: utf-8 -*-

import pytest
from xTool.cython.bytes_order import (endian_uchar_to_bytes, endian_ushort_to_bytes, endian_uint_to_bytes)


def test_endian_uchar_to_bytes():
    actual = endian_uchar_to_bytes(0x12)
    assert len(actual) == 1
    assert actual.hex() == "12"

    with pytest.raises(OverflowError):
        endian_uchar_to_bytes(0x1234)


def test_endian_ushort_to_bytes():
    actual = endian_ushort_to_bytes(0x1234)
    assert len(actual) == 2
    assert actual.hex() == "1234"


def test_endian_uint_to_bytes():
    actual = endian_uint_to_bytes(0x12345678)
    assert len(actual) == 4
    assert actual.hex() == "12345678"
