#coding: utf-8

import base64

from xTool.crypto.fernet import *


def test_generate_fernet_key():
    key = generate_fernet_key()
    assert type(key) == type(u'')
    assert len(base64.b64decode(key.encode('utf8'))) == 32
