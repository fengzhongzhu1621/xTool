import struct

import pytest


@pytest.mark.skip
class TestBytesOrder:
    def test_endian_uchar_to_bytes(self):
        from xTool.ffi.cython.bytes_order import endian_uchar_to_bytes

        actual = endian_uchar_to_bytes(0x12)
        assert len(actual) == 1
        assert actual.hex() == "12"

        with pytest.raises(OverflowError):
            endian_uchar_to_bytes(0x1234)

    def test_endian_ushort_to_bytes(self):
        from xTool.ffi.cython.bytes_order import endian_ushort_to_bytes

        actual = endian_ushort_to_bytes(0x1234)
        assert len(actual) == 2
        assert actual.hex() == "1234"

    def test_endian_uint_to_bytes(self):
        from xTool.ffi.cython.bytes_order import endian_uint_to_bytes

        actual = endian_uint_to_bytes(0x12345678)
        assert len(actual) == 4
        assert actual.hex() == "12345678"

    def test_endian_byte_to_uchar(self):
        from xTool.ffi.cython.bytes_order import endian_byte_to_uchar

        package = struct.pack(">B", 0x12)
        assert package.hex() == "12"
        actual = endian_byte_to_uchar(package)
        assert actual == 0x12

    def test_endian_byte_to_ushort(self):
        from xTool.ffi.cython.bytes_order import endian_byte_to_ushort

        package = struct.pack(">H", 0x1234)
        assert package.hex() == "1234"
        actual = endian_byte_to_ushort(package)
        assert actual == 0x1234

    def test_endian_byte_to_uint(self):
        from xTool.ffi.cython.bytes_order import endian_byte_to_uint

        package = struct.pack(">I", 0x12345678)
        assert package.hex() == "12345678"
        actual = endian_byte_to_uint(package)
        assert actual == 0x12345678
