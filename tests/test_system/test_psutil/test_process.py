import psutil


def test_pids():
    # 获取当前运行的所有进程ID
    pids = psutil.pids()

    for pid in pids:
        try:
            process = psutil.Process(pid)
            print(f"Process ID: {pid}, Name: {process.name()}, CPU: {process.cpu_percent()}%")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
