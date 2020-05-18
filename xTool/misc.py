# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import re
import sys
from datetime import datetime, date
import json
import platform
import traceback
import subprocess
import random

import numpy as np
import psutil


# Determine platform being used.
system = platform.system()
USE_MAC = USE_WINDOWS = USE_X11 = False
if system == 'Darwin':
    USE_MAC = True
elif system == 'Windows' or system == 'Microsoft':
    USE_WINDOWS = True
else:  # Default to X11
    USE_X11 = True


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3

if PY3:
    xrange = range


def get_encodings():
    yield 'utf8'
    from locale import getpreferredencoding
    prefenc = getpreferredencoding()
    if prefenc:
        yield prefenc

        prefenc = {
            'latin1': 'latin9',
            'iso-8859-1': 'iso8859-15',
            'cp1252': '1252',
        }.get(prefenc.lower())
        if prefenc:
            yield prefenc


def exceptionToString():
    exc = sys.exc_info()
    return "".join(traceback.format_exception(*exc))


def tob(s, enc='utf-8'):
    """将字符串转换为utf8/bytes编码 ."""
    return s.encode(enc) if not isinstance(s, bytes) else s


def tou(s, enc='utf-8'):
    """将字符串转换为unicode编码 ."""
    return s.decode(enc) if isinstance(s, bytes) else s


def get_cur_info(number=1):
    """
        返回(调用函数名, 行号)
    """
    frame = sys._getframe(number)
    return (frame.f_code.co_name, frame.f_lineno)


def runCommand(command):
    print(command)
    proc = subprocess.Popen(command,
        shell=True,
        close_fds=False if USE_WINDOWS else False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    (stdoutdata, stderrdata) = proc.communicate()
    if stdoutdata:
        print(stdoutdata)
    if stderrdata:
        print(stderrdata)
    assert not proc.returncode


def getRunCommandResult(command):
    proc = subprocess.Popen(command,
        shell=True,
        close_fds=False if USE_WINDOWS else False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    (stdoutdata, stderrdata) = proc.communicate()
    return (proc.returncode, stdoutdata, stderrdata)


def get_local_host_ip(ifname=b'eth1'):
    """获得本机的IP地址 ."""
    import platform
    import socket
    if platform.system() == 'Linux':
        import fcntl
        import struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        o_ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,
            struct.pack('256s', ifname[:15])
        )[20:24])
    else:
        o_ip = socket.gethostbyname(socket.gethostname())
    return o_ip


def json_ser(obj):
    """json serializer that deals with dates.

    usage: json.dumps(object, default=utils.json.json_ser)
    """
    if isinstance(obj, (datetime, date)):
        # Return a string representing the date and time in ISO 8601 format,
        # YYYY-MM-DDTHH:MM:SS.mmmmmm or, if microsecond is 0, YYYY-MM-DDTHH:MM:SS
        return obj.isoformat()


class NumpyJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        # convert dates and numpy objects in a json serializable format
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif type(obj) in (np.int_, np.intc, np.intp, np.int8, np.int16,
                           np.int32, np.int64, np.uint8, np.uint16,
                           np.uint32, np.uint64):
            return int(obj)
        elif type(obj) in (np.bool_,):
            return bool(obj)
        elif type(obj) in (np.float_, np.float16, np.float32, np.float64,
                           np.complex_, np.complex64, np.complex128):
            return float(obj)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def listData(rows, key, value):
    """
        将两个字段转换为词典格式
    """
    result = {}
    for row in rows:
        result[row[key]] = row[value]
    return result


def getFileLines(path):
    """
        获得文件行数
    """
    (returncode, stdoutdata, stderrdata) = getRunCommandResult("wc -l %s" % path)
    if returncode == 0 and stdoutdata:
        return int(stdoutdata.split(' ')[0])
    return 0


def getDirLines(path, pattern=None):
    """
        获得目录下文件名符合pattern规则的文件行数
    """
    import fnmatch
    lines = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for file_name in filenames:
            full_path = os.path.join(dirpath, file_name)
            if not pattern or fnmatch.fnmatch(file_name, pattern):
                lines += getFileLines(full_path)
    return lines


def isMemoryAvailable(limit=80):
    """检查内存空间是否可用 """
    virtualMemory = psutil.virtual_memory()
    percent = virtualMemory.percent
    if percent > limit:
        return False
    return True


def isDiskAvailable(dirname, limit=80):
    """检查磁盘空间是否可用 """
    diskUsage = psutil.disk_usage(dirname)
    percent = diskUsage.percent
    if percent > limit:
        return False
    return True


def format_row(row):
    """日志行按空白字符分隔 """
    lines = re.split("\s", row.strip())
    return [i for i in lines if i]


def get_col_count(row):
    """获得文本列数 """
    return len(format_row(row))


def get_file_rowcol_count(filePath):
    """ 获得文件行数和列数
        - 忽略空行
        - 根据第一行识别列数
    """
    row = 0
    col = 0
    with open(filePath , 'r') as fb:
        for line in fb:
            line = line.strip()
            if line:
                row += 1
                # 根据第一行识别列数
                if row == 1:
                    col = get_col_count(line)
    return (row, col)


def get_file_row(filePath):
    """获得文件行数 ."""
    with open(filePath, 'r') as rFb:
        return sum(1 for row in rFb if row.strip())


if PY2:
    from itertools import izip_longest as zip_longest  # for Python 2.x
else:
    from itertools import zip_longest # for Python 3.x
# from six.moves import zip_longest # for both (uses the six compat library)


def grouper(n, iterable, padvalue=None):
    """grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"""
    return zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    return (l[i:i + n] for i in xrange(0, len(l), n))


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Returns a securely generated random string.

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    return ''.join([random.choice(allowed_chars) for i in range(length)])


def print_bin(data):
    """以比较整齐的格式打印二进制数据，用于设计二进制数据的调试过程

        >>> print_bin("\x00\x01\x31\x32\x44hdj139")
        >>> 0000: 00 01 31 32 44 68 64 6a 31 33 39 74 65 6e 63 65  ..12Dhdj139

        `code source <http://code.oa.com/v2/weima/detail/70493>`_

    """
    assert isinstance(data, basestring)

    dump_list = []
    slice = ""
    addr = 0

    for byte in data:
        if addr % 16 == 0:
            dump_list.append(" ")

            for char in slice:
                if ord(char) >= 32 and ord(char) <= 126:
                    dump_list.append(char)
                else:
                    dump_list.append(".")

            dump_list.append("\n%04x: " % addr)
            slice = ""

        dump_list.append("%02x " % ord(byte))
        slice += byte
        addr += 1

    remainder = addr % 16

    if remainder != 0:
        dump_list.append("   " * (16 - remainder) + " ")

    for char in slice:
        if ord(char) >= 32 and ord(char) <= 126:
            dump_list.append(char)
        else:
            dump_list.append(".")

    print("".join(dump_list))


def ipv4_into_int(ip):
    # 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“.”后转成10进制的 3232235789 即可。
    # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    return reduce(lambda x,y:(x<<8)+y,map(int,ip.split('.')))


def strict_bool(s):
    """
    Variant of bool() that only accepts two possible string values.
    """
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError( s )


def less_strict_bool( x ):
    """
    Idempotent and None-safe version of strict_bool.
    """
    if x is None:
        return False
    elif x is True or x is False:
        return x
    else:
        return strict_bool( x )


def properties( obj ):
    """
    获得一个对象的所有属性值

    Returns a dictionary with one entry per attribute of the given object. The key being the
    attribute name and the value being the attribute value. Attributes starting in two
    underscores will be ignored. This function is an alternative to vars() which only returns
    instance variables, not properties. Note that methods are returned as well but the value in
    the dictionary is the method, not the return value of the method.

    >>> class Foo():
    ...     def __init__(self):
    ...         self.var = 1
    ...     @property
    ...     def prop(self):
    ...         return self.var + 1
    ...     def meth(self):
    ...         return self.var + 2
    >>> foo = Foo()
    >>> properties( foo ) == { 'var':1, 'prop':2, 'meth':foo.meth }
    True

    Note how the entry for prop is not a bound method (i.e. the getter) but a the return value of
    that getter.
    """
    return dict( (attr, getattr( obj, attr ))
                     for attr in dir( obj )
                     if not attr.startswith( '__' ) )


def get_first_duplicate(items):
    """获得列表中第一个重复值 ."""
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
        else:
            return item
    return None


def many_to_one(input_dict):
    """拆分词典中的key
    Convert a many-to-one mapping to a one-to-one mapping
    
    Examples:

        {'ab': 1, ('c', 'd'): 2} -> {'a': 1, 'b': 1, 'c': 2, 'd': 2}
    
    """
    return dict((key, val)
                for keys, val in input_dict.items()
                for key in keys)


def open_url(url):
    """根据URL打开浏览器 ."""
    from webbrowser import open as wbopen
    wbopen(url)


def format_exception(exc):
    """
    Format and return the specified exception information as a string.

    This default implementation just uses
    traceback.print_exception()
    """
    ei = (type(exc), exc, exc.__traceback__)
    sio = io.StringIO()
    tb = ei[2]
    traceback.print_exception(ei[0], ei[1], tb, None, sio)
    s = sio.getvalue()
    sio.close()
    if s[-1:] == "\n":
        s = s[:-1]
    return s


def format_exception_without_line_break(exc):
    """将异常对象转换为没有换行的字符串 ."""
    s = format_exception(exc)
    return s.replace("\n", "\\n")


def make_int(value):
    """将值转换为int类型 ."""
    if value is not None and not isinstance(value, (int, float)):
        return int(value)
    return value
