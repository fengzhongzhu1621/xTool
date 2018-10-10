#coding: utf-8


def generate_fernet_key():
    """生成一个44字节的随机数 ."""
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        pass
    try:
        # 产生了一个44字节的随机数，并用base64编码，并解码为unicode编码
        key = Fernet.generate_key().decode()
    except NameError:
        key = "cryptography_not_found_storing_passwords_in_plain_text"
    return key
