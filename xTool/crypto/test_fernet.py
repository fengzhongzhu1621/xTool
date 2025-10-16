import sys

from xTool.crypto import fernet

PY3 = sys.version_info[0] == 3


def test_generate_fernet_key():
    key = fernet.generate_fernet_key()
    assert len(key) == 44


def test_encrypt():
    key = fernet.generate_fernet_pbkdf2hmac_key()
    plaintext = "hello world"
    ciphertext = fernet.encrypt(key, plaintext)
    plaintext2 = fernet.decrypt(key, ciphertext)
    assert plaintext == plaintext2

    plaintext = "hello world"
    ciphertext = fernet.encrypt(key, plaintext)
    plaintext2 = fernet.decrypt(key, ciphertext)
    assert plaintext == plaintext2

    plaintext = "你好"
    ciphertext = fernet.encrypt(key, plaintext)
    plaintext2 = fernet.decrypt(key, ciphertext)
    assert plaintext == plaintext2

    plaintext = "你好"
    ciphertext = fernet.encrypt(key, plaintext)
    plaintext2 = fernet.decrypt(key, ciphertext)
    if PY3:
        assert str(plaintext) == plaintext2
    else:
        assert plaintext.decode("utf8") == plaintext2


def test_double_decrypt():
    # 生成根秘钥
    root_key = fernet.generate_fernet_pbkdf2hmac_key()
    # 生成实例秘钥
    instance_key = fernet.generate_fernet_pbkdf2hmac_key()
    # 使用根秘钥加密实例秘钥
    instance_key_cipher = fernet.encrypt(root_key, instance_key)
    plaintext = "你好"
    # 加密密码
    cipher_text = fernet.double_encrypt(root_key, instance_key_cipher, plaintext)
    # 使用根秘钥和实例秘钥密文解密
    plaintext2 = fernet.double_decrypt(root_key, instance_key_cipher, cipher_text)
    assert plaintext == plaintext2


def test_parseDbConfig():
    # 生成根秘钥
    root_key = fernet.generate_fernet_pbkdf2hmac_key()
    # 生成实例秘钥
    instance_key = fernet.generate_fernet_pbkdf2hmac_key()
    # 使用根秘钥加密实例秘钥
    instance_key_cipher = fernet.encrypt(root_key, instance_key)
    password = "123456"
    db_config = {
        "db_my_db": {
            "host": "localhost",
            "user": "root",
            "password": fernet.encrypt(instance_key, password),
            "database": "db_my_db",
            "charset": "utf8",
            "root_key": root_key,
            "instance_key_cipher": instance_key_cipher,
        }
    }
    conf = fernet.parse_db_config(db_config.get("db_my_db"))
    assert password == conf[3]
