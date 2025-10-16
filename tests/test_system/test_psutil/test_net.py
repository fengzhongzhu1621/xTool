import psutil


def test_net_io_counters():
    # 获取网络接口的发送和接收数据量
    net_io = psutil.net_io_counters()
    print(f"Bytes Sent: {net_io.bytes_sent}, Bytes Received: {net_io.bytes_recv}")
