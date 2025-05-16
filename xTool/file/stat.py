import os
import time


def get_file_modified_date(file_path: str):
    """返回存在的文件的最后修改日期"""
    # 获取文件的最后修改时间
    timestamp = os.stat(file_path).st_mtime
    return time.strftime("%Y.%m.%d", time.localtime(timestamp))
