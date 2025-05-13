import resource
import time


def test_setrlimit_cpu():
    """设置进程的资源限制"""
    # 限制程序的CPU时间为2秒，如果程序运行超过这个时间，系统会终止它
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))

    # 测试代码：让程序运行超过2秒
    print("程序开始执行")
    time.sleep(3)
    print("程序执行完成")


def test_setrlimit_memory():
    # 设置最大内存使用为100MB
    resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024))

    # 尝试分配200MB内存
    try:
        _ = [0] * (200 * 1024 * 1024)
    except MemoryError:
        print("内存限制已达到，程序被终止")


def test_setrlimit_file_handler():
    """设置程序允许打开的最大文件数。"""
    # 设置最大文件句柄数为5
    resource.setrlimit(resource.RLIMIT_NOFILE, (5, 5))

    # 测试代码：打开超过5个文件
    files = []
    try:
        for i in range(10):
            f = open(f"file_{i}.txt", "w")
            files.append(f)
    except OSError:
        print("文件打开超过限制")


def test_setrlimit_stack():
    # 设置最大栈大小为1MB
    resource.setrlimit(resource.RLIMIT_STACK, (1 * 1024 * 1024, 1 * 1024 * 1024))

    # 递归调用
    def recursive_function(n):
        if n > 0:
            return recursive_function(n - 1)
        return n

    try:
        recursive_function(100000)
    except RecursionError:
        print("栈溢出，程序被终止")
