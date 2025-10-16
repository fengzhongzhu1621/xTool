import threading

from xTool.utils.threads import defaultlocal, go


def test_defaultlocal():
    local = defaultlocal(foo=42)

    def f():
        assert local.foo == 42

    thread = threading.Thread(target=f)
    thread.start()
    thread.join()


@go
def add(a: int, b: int) -> int:
    print(f"{a} + {b} = {a + b}")


def test_go():
    t = add(1, 2)
    t.join()
    t = add(10, 20)
    t.join()
