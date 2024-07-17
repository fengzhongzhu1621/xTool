import psutil


def test_cpu_percent():
    # 获取CPU的利用率，参数interval表示时间间隔，单位为秒
    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_usage} %")
