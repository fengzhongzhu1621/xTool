#coding: utf-8

import base64

from xTool.crypto.fernet import *


def test_generate_fernet_key():
    key = generate_fernet_key()
    assert type(key) is type(u'')
    assert len(key) == 44
