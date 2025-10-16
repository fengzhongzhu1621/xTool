import psutil


def test_virtual_memory():
    # 获取内存的总量、使用量、空闲量等信息
    memory = psutil.virtual_memory()
    print(f"Total: {memory.total}, Used: {memory.used}, Free: {memory.free}")
