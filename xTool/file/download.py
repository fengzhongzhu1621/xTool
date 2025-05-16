import hashlib
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def download_file(
    url: str,
    destination: str = None,
    chunk_size: int = 1024 * 1024,  # 1MB分块
    retries: int = 3,
    timeout: float = 30.0,
    headers=None,
    verify_checksum: str = None,
    session=None,
) -> dict:
    """
    增强版文件下载函数

    :param url: 下载地址
    :param destination: 保存路径（默认使用URL最后一段）
    :param chunk_size: 下载分块大小（默认1MB）
    :param retries: 失败重试次数
    :param timeout: 请求超时时间
    :param headers: 自定义请求头
    :param verify_checksum: 期望的MD5校验值
    :param session: 可复用的requests.Session对象
    :return: 包含下载信息的字典 {'path', 'size', 'md5'}
    """

    # 初始化会话
    session = session or requests.Session()
    retry_strategy = Retry(total=retries, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
    session.mount("http://", HTTPAdapter(max_retries=retry_strategy))

    # 自动推断文件名
    if not destination:
        destination = os.path.basename(url).split('?')[0]
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    # 断点续传支持
    file_mode = "ab" if os.path.exists(destination) else "wb"
    headers = headers if headers else {}
    headers = {**headers, 'Range': f'bytes={os.path.getsize(destination)}-'} if os.path.exists(destination) else None

    if verify_checksum:
        md5_hash = hashlib.md5()

    total_bytes = 0

    try:
        with session.get(url, headers=headers or {}, stream=True, timeout=timeout) as response:
            response.raise_for_status()

            # 处理不支持断点续传的情况
            if response.status_code == 200 and os.path.exists(destination):
                os.remove(destination)
                file_mode = "wb"

            with open(destination, mode=file_mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        if verify_checksum:
                            md5_hash.update(chunk)
                        total_bytes += len(chunk)
        result = {
            'path': os.path.abspath(destination),
            'size': total_bytes,
            'md5': md5_hash.hexdigest() if verify_checksum else None,
        }

        if verify_checksum and result['md5'] != verify_checksum:
            os.remove(destination)
            raise ValueError("File checksum verification failed")

        return result

    except Exception as e:
        if os.path.exists(destination):
            os.remove(destination)
        raise RuntimeError(f"Download failed: {str(e)}") from e
