# -*- coding: utf-8 -*-

import struct
from random import randint
import hashlib
import hmac


class SecurityManager(object):
    """
        SecurityManager provides private keys, hashing and encryption functions
    """
    def __init__(self, validationKey=None, encryptionKey=None, hashAlgorithm=hashlib.sha1, cryptAlgorithm='des'):
        self.hashAlgorithm  = hashAlgorithm
        self.cryptAlgorithm = cryptAlgorithm
        self._validationKey = validationKey
        self._encryptionKey = encryptionKey

    def generateRandomKey(self):
        """
            Generate a randomly validation key
        """
        maxsize = 2 ** (struct.Struct('i').size * 8 - 1) - 1
        return '%08x%08x%08x%08x' % (randint(0, maxsize), randint(0, maxsize), randint(0, maxsize), randint(0, maxsize))

    def getValidationKey(self):
        """
            Get the validationKey used to generate HMAC
            If the key is not explicitly set, a random one is generated and returned
        """
        if self._validationKey:
            return self._validationKey
        else:
            key = self.generateRandomKey()
            self.setValidationKey(key)
            return self._validationKey

    def setValidationKey(self, value):
        """
            Set the validationKey used to generate HMAC
        """
        if value:
            self._validationKey = value;

    def computeHMAC(self, data, key=None):
        """
            HMAC是密钥相关的哈希运算消息认证码（keyed-Hash Message Authentication Code）
            HMAC运算利用哈希算法，以一个密钥和一个消息为输入，生成一个消息摘要作为输出。
            Computes the HMAC for the data with {getValidationKey ValidationKey}.
            @data: data to be generated HMAC
            @key the private key to be used for generating HMAC. Defaults to null, meaning using {@link validationKey}.
            return the HMAC for the data
        """
        if not key:
            key = self.getValidationKey()
        key = key.encode('utf8') if not isinstance(key, bytes) else key
        data = data.encode('utf8') if not isinstance(data, bytes) else data
        return hmac.new(key, data, self.hashAlgorithm).hexdigest()

    def validateData(self, data, key=None):
        """
            验证数据是否合法
        """
        hmacLen = len(self.computeHMAC('test'))
        if len(data) >= hmacLen:
            # 双重加密
            hmacValue = data[:hmacLen]
            data2     = data[hmacLen:]
            if hmacValue == self.computeHMAC(data2, key):
                return data2
            else:
                return False
        else:
            return False

    def createHmac(self, data, key=None):
        newdata = ""
        for (name, value) in data.items():
            newdata += str(name) + str(value)
        return self.computeHMAC(newdata, key)

    def verifyHmac(self, data, parameter='_', key=None):
        hmacValue = data.get(parameter)
        if not hmacValue:
            return False
        data.pop(parameter)
        return self.createHmac(data, key) == hmacValue
