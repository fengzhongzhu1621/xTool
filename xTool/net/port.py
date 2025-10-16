import socket
from typing import List, Tuple

from xTool.exceptions import PortInvalidError


def is_port_valid(port: int) -> bool:
    if 0 <= int(port) <= 65535:
        return True
    else:
        return False


def is_unix_socket(port: int) -> bool:
    if int(port) == 0:
        return True
    else:
        return False


def format_port(port: str) -> str:
    """格式化端口字符串 ."""
    if not port:
        return ""
    if "ALL" in port.upper():
        return "0-65535"
    # 计算端口范围
    port_range_list = port_range(port)
    result = []
    for port_num_min, port_num_max in port_range_list:
        if port_num_min == port_num_max:
            result.append(str(port_num_min))
        else:
            result.append(f"{port_num_min}-{port_num_max}")

    port = ";".join(result)

    return port


def port_range(port: str) -> List[Tuple[int, int]]:
    """
    将端口范围字符串解析为结构化数据
    :return: 二元组列表，元组的两个元素分别代表起始端口和结束端口（闭区间）
    :example [(1, 1), (3, 5), (7, 10)]
    """

    port_range_list = []

    # 为空直接返回
    if not port:
        return port_range_list

    try:
        # 按分隔符拆分
        range_str_list = [p.strip() for p in port.split(";") if p.strip()]
        for range_str in range_str_list:
            try:
                # 先判断是不是单个数字
                port_num = parse_port_num(range_str)
                # 如果是单个数字，则转化为区间并保存
                port_range_list.append((port_num, port_num))
            except ValueError:
                # 如果不是单个数字，尝试识别为区间字符串
                port_range_tuple = range_str.split("-")

                # 尝试拆分为上界和下界
                if len(port_range_tuple) != 2:
                    raise ValueError("不合法的端口范围定义格式：{}".format(range_str))

                # 对上界和下界分别进行解析
                port_num_min, port_num_max = port_range_tuple
                port_num_min = parse_port_num(port_num_min)
                port_num_max = parse_port_num(port_num_max)

                if port_num_min > port_num_max:
                    # 下界 > 上界 也是不合法的范围
                    raise ValueError("不合法的端口范围定义格式：{}".format(range_str))
                port_range_list.append((port_num_min, port_num_max))

    except Exception as exc_info:  # pylint: disable=broad-except
        raise ValueError("端口范围字符串解析失败：{}".format(exc_info))

    return port_range_list


def parse_port_num(port_num: str) -> int:
    """
    检查端口号是否合法
    """
    if isinstance(port_num, str) and port_num.strip().isdigit():
        port_num = int(port_num)
    elif isinstance(port_num, int):
        pass
    else:
        raise ValueError("无法解析的端口号：{}".format(port_num))

    if 0 <= port_num <= 65535:
        return port_num

    raise ValueError("不在合法范围内的端口号：{}".format(port_num))


def is_tcp_port_open(ip, port) -> bool:
    """判断端口是否占用 ."""
    sock = None
    try:
        if not is_port_valid(port):
            raise PortInvalidError("端口%s无效" % ip)
        sock = new_socket(ip, stream=True)
        # 出错时返回出错码,而不是抛出异常
        result = sock.connect_ex((ip, port))
        if result == 0:
            # 地址可以访问，说明端口已经被占用
            return False
        return True
    finally:
        if sock:
            sock.close()


def is_udp_port_open(ip, port) -> bool:
    """判断端口是否占用 ."""
    sock = None
    try:
        if not is_port_valid(port):
            raise PortInvalidError("端口%s无效" % ip)
        sock = new_socket(ip, stream=False)
        sock.bind((ip, port))
        return True
    except Exception:  # pylint: disable=broad-except
        return False
    finally:
        if sock:
            sock.close()


def get_unused_port() -> int:
    """获得本地未使用的端口号 ."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", 0))
        port = sock.getsockname()[-1]
    return port
