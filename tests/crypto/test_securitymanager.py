#coding: utf-8

import hashlib

from xTool.crypto.securitymanager import SecurityManager


class TestSecurityManager:
    manager = SecurityManager("validationKey", hashAlgorithm=hashlib.sha1)

    def test_generateRandomKey(self):
        actual = self.manager.generateRandomKey()
        assert len(actual) == 32

    def test_setValidationKey(self):
        key = "validationKey_2"
        self.manager.setValidationKey(key)
        assert self.manager.getValidationKey() == key

    def test_computeHMAC(self):
        key = "validationKey_1"
        data = 'data'
        actual = self.manager.computeHMAC(data, key)
        expect = "04da5c206fed9d4b6d716fb71db8e3e09d56eb71"
        assert expect == actual
        actual = self.manager.computeHMAC(data)
        expect = "0d5956c831a9f20e26df34fcdb4ff6061c7ad92a"
        assert expect == actual

    def test_createHmac(self):
        data1 = {'a': "Hello world"}
        actual = self.manager.createHmac(data1, key="4503c915196ca37900e8614c7407e2cc")
        expect = "63630ce946d73e42c03f4df882e18c91dcad7121"
        assert actual == expect

    def test_verifyHmac(self):
        data2 = {'a': "Hello world", '_' : "63630ce946d73e42c03f4df882e18c91dcad7121"}
        actual = self.manager.verifyHmac(data2, '_', key="4503c915196ca37900e8614c7407e2cc")
        assert actual is True
