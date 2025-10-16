"""
基于fernet的加解密算法
"""

import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from xTool.exceptions import XToolException
from xTool.misc import tob
from xTool.utils.log.logging_mixin import LoggingMixin

InvalidFernetToken = InvalidToken
_fernet = None


def generate_fernet_key():
    """产生了一个44字节的随机数，并用base64编码，并解码为unicode编码 ."""
    key = Fernet.generate_key().decode()
    return key


def generate_fernet_pbkdf2hmac_key():
    salt = os.urandom(16)
    password = os.urandom(64)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt(key, plaintext):
    f = Fernet(tob(key))
    return f.encrypt(tob(plaintext)).decode('utf-8')


def decrypt(key, ciphertext):
    f = Fernet(tob(key))
    return f.decrypt(tob(ciphertext)).decode('utf-8')


def double_encrypt(root_key, instance_key_cipher, plaintext):
    instance_key = decrypt(root_key, instance_key_cipher)
    cipher_text = encrypt(instance_key, plaintext)
    return cipher_text


def double_decrypt(root_key, instance_key_cipher, cipher_text):
    instance_key = decrypt(root_key, instance_key_cipher)
    return decrypt(instance_key, cipher_text)


def parse_db_config(
    db_config, root_key=None, instance_key_cipher=None, max_idle_time=7 * 3600, connect_timeout=5, time_zone="+0:00"
):
    """用于将db配置转换成torndb可识别的参数格式 ."""
    host = db_config.get('host')
    user = db_config.get('user')
    password = db_config.get('password')
    if not password:
        password = db_config.get('passwd')
    root_key = root_key if root_key else db_config.get('root_key')
    instance_key_cipher = instance_key_cipher if instance_key_cipher else db_config.get('instance_key_cipher')
    if password and root_key and instance_key_cipher:
        password = double_decrypt(root_key, instance_key_cipher, password)
    charset = db_config.get('charset', 'utf8')
    database = db_config.get('database')
    if not database:
        database = db_config.get('db')
    return host, database, user, password, max_idle_time, connect_timeout, time_zone, charset


def get_fernet(fernet_key):
    """
    Deferred load of Fernet key.

    This function could fail either because Cryptography is not installed
    or because the Fernet key is invalid.

    :return: Fernet object
    :raises: XToolException if there's a problem trying to load Fernet
    """
    global _fernet
    if _fernet:
        return _fernet

    if not fernet_key:
        log = LoggingMixin().log1
        log.warning("empty cryptography key - values will not be stored encrypted.")
        raise XToolException("Could not create Fernet object")
    else:
        _fernet = Fernet(fernet_key.encode('utf-8'))
        _fernet.is_encrypted = True
        return _fernet
