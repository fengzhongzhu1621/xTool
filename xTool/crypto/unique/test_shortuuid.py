"""
shortuuid 用于生成简短的、唯一的、URL安全、线程安全 的字符串
"""

import uuid

import shortuuid


def test_uuid():
    actual = shortuuid.uuid()
    # print(actual) # ZocGPTZQddDsDwtMESFdFw
    assert len(actual) == 22


def test_uuid_with_len():
    """生成指定长度的短 uuid"""
    actual = shortuuid.ShortUUID().random(length=10)
    assert len(actual) == 10


def test_decode():
    """转换为原始的uuid"""
    u = uuid.uuid4()

    # 转换未短的 uuid
    s = shortuuid.encode(u)

    # 还原为原始的 uuid
    old = shortuuid.decode(s)

    assert u == old


def test_set_alphabet():
    """自定义字母表 ."""
    alphabet = "abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWZYZ-_"

    shortuuid.set_alphabet(alphabet=alphabet)
    shortuuid.uuid()

    shortuuid.ShortUUID(alphabet=alphabet).uuid()
