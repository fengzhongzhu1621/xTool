# coding: utf-8

import threading
from xTool.utils.threads import defaultlocal


def test_defaultlocal():
    local = defaultlocal(foo=42)

    def f():
        assert local.foo == 42

    thread = threading.Thread(target=f)
    thread.start()
    thread.join()
