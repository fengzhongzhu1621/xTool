#coding: utf-8
from datetime import datetime
from datetime import date
import time
import json

import numpy as np

from xTool.utils.json import *


def test_json_ser():
    now1 = datetime.now()
    now2 = date.fromtimestamp(time.time())
    a = {
        'a': 1,
        'now1': now1, 
        'now2': now2, 
    }
    actual = json.dumps(a, default=json_ser)


def test_XToolJsonEncoder():
    now1 = datetime.now()
    now2 = date.fromtimestamp(time.time())
    bool_value = np.bool(1)
    int_value = np.int8(1.1)
    float_value = np.float(True)
    b = {
        'a': 1,
        'now1': now1, 
        'now2': now2, 
        'bool_value': bool_value,
        'int_value': int_value, 
        'float_value': float_value
    }
    actual = json.dumps(b, cls=XToolJsonEncoder)
