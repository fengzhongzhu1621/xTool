# -*- coding: utf-8 -*-
import uuid


def uniqid():
    return uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex


def uniqid4():
    return str(uuid.uuid4())
