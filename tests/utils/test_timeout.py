#coding: utf-8

import time
import sys

import pytest

from xTool.utils.timeout import timeout
from xTool.exceptions import XToolTaskTimeout


@pytest.mark.skipif(sys.platform == 'win32', reason="requires windows")
def test_timeout():
    with timeout(1):
        pass
    with pytest.raises(XToolTaskTimeout):
        with timeout(1):
            time.sleep(2)
