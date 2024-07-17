import psutil


def test_disk_partitions():
    # 获取磁盘的分区信息
    disk_partitions = psutil.disk_partitions()
    for partition in disk_partitions:
        print(f"Device: {partition.device}, Type: {partition.fstype}, Total: {partition.total}, Free: {partition.free}")
