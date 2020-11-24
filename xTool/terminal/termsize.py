# -*- coding: utf-8 -*-

import os
import struct
import subprocess
import shlex
from xTool.misc import USE_MAC, USE_WINDOWS, USE_LINUX, USE_CYGWIN


def ioctl_GWINSZ(fd):
    try:
        import fcntl
        import termios
        cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        return cr
    except Exception:
        pass


def get_windows_terminal_size():
    from ctypes import windll, create_string_buffer
    # 获得stderr文件句柄
    hander = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    # 获取特定的控制台屏幕缓冲区信息
    is_ok = windll.kernel32.GetConsoleScreenBufferInfo(hander, csbi)
    if is_ok:
        _, _, _, _, _, left, top, right, bottom, _, _ = struct.unpack(
            "hhhhHhhhhhh", csbi.raw)
        size_x = right - left + 1
        size_y = bottom - top + 1
        return size_x, size_y
    else:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return cols, rows


def get_linux_terminal_size():
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except Exception:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except Exception:
            return None
    return int(cr[1]), int(cr[0])


def get_terminal_size():
    if USE_WINDOWS:
        return get_windows_terminal_size()
    if USE_MAC or USE_LINUX or USE_CYGWIN:
        return get_linux_terminal_size()
    return 80, 25


if __name__ == "__main__":
    size_x, size_y = get_terminal_size()
    print("Width: {}, Height: {}".format(size_x, size_y))
