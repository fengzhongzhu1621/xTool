from core.tasks import run_sub_task


def sub_task(a, b):
    return a + b


def test_run_sub_task():
    actual = run_sub_task("task_1", sub_task, "sub_task", 1, 2)
    expect = 3
    assert actual == expect
