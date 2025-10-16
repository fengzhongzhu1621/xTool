import hashlib
import hmac
import sys
from random import randint
from typing import Optional


class UrlHmacManager:
    def __init__(
        self, validation_key: Optional[str] = None, encryption_key: Optional[str] = None, hash_algorithm=hashlib.sha512
    ):
        self.hash_algorithm = hash_algorithm
        self._validation_key = validation_key
        self._encryption_key = encryption_key

    @staticmethod
    def generate_random_key():
        maxint = sys.maxsize
        return '{:08x}{:08x}{:08x}{:08x}'.format(
            randint(0, maxint), randint(0, maxint), randint(0, maxint), randint(0, maxint)
        )

    def get_validation_key(self):
        """
        Get the validationKey used to generate HMAC
        If the key is not explicitly set, a random one is generated and returned
        """
        if self._validation_key:
            return self._validation_key
        else:
            key = self.generate_random_key()
            self.set_validation_key(key)
            return self._validation_key

    def set_validation_key(self, value):
        """
        Set the validationKey used to generate HMAC
        """
        if value:
            self._validation_key = value

    def compute_hmac(self, data, key=None):
        """
        HMAC是密钥相关的哈希运算消息认证码（keyed-Hash Message Authentication Code）
        HMAC运算利用哈希算法，以一个密钥和一个消息为输入，生成一个消息摘要作为输出。
        """
        if not key:
            key = self.get_validation_key()
        return hmac.new(key.encode(), data.encode(), self.hash_algorithm).hexdigest()

    def validate_data(self, data, key=None):
        """验证数据是否合法 ."""
        hmac_len = len(self.compute_hmac('test'))
        if len(data) >= hmac_len:
            # 双重加密
            hmac_value = data[:hmac_len]
            data2 = data[hmac_len:]
            if hmac_value == self.compute_hmac(data2, key):
                return data2
            else:
                return False
        else:
            return False

    def create_hmac(self, data, key=None):
        new_data = ""
        for name, value in data.items():
            new_data = "{}{}{}".format(new_data, str(name), str(value))
        return self.compute_hmac(new_data, key)

    def verify_hmac(self, data, parameter='_', key=None):
        hmac_value = data.get(parameter)
        if not hmac_value:
            return False
        data.pop(parameter)
        return self.create_hmac(data, key) == hmac_value
