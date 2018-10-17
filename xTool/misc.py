# -*- coding: utf-8 -*-
"""
    各种工具集
"""

import os
import subprocess
import sys
try:
    import pexpect
except ImportError:
    pass
import datetime
import socket
try:
    import fcntl
except ImportError:
    pass
import struct
import traceback
try:
    import psutil
except ImportError:
    pass
import re
import platform
import random
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import decimal
from functools import wraps


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if sys.version > '3':
    unicode = str
    unichr = chr


# Determine platform being used.
system = platform.system()
USE_MAC = USE_WINDOWS = USE_X11 = False
if system == 'Darwin':
    USE_MAC = True
elif system == 'Windows' or system == 'Microsoft':
    USE_WINDOWS = True
else:  # Default to X11
    USE_X11 = True


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


def ustr(value):
    """
    @value : the value to convert
    @return: unicode string
    """
    orig = value
    if isinstance(value, unicode):
        return value

    try:
        return tou(value)
    except Exception as e:
        pass

    for ln in get_encodings():
        try:
            return tou(value, ln)
        except Exception as e:
            pass
    raise UnicodeError('unable de to convert %r' % (orig,))


def get_cur_info(number=1):
    """
        返回(调用函数名, 行号)
    """
    frame = sys._getframe(number)
    return (frame.f_code.co_name, frame.f_lineno)


def runCommand(command):
    """
        运行系统命令
    """
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
    # for line in stdoutdata:
    #    print(line.strip())
    # for line in stderrdata:
    #    print(line.strip())
    assert not proc.returncode


def getRunCommandResult(command):
    """
        获得系统命令的运行结果
    """
    proc = subprocess.Popen(command,
        shell=True,
        close_fds=False if USE_WINDOWS else False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    (stdoutdata, stderrdata) = proc.communicate()
    return (proc.returncode, stdoutdata, stderrdata)


class ExpectTimeoutException(Exception):
    pass


ScpSyncTimeoutException = ExpectTimeoutException


class ScpPasswordException(Exception):
    pass


PasswordException = ScpPasswordException


class ScpNoSuchFileException(Exception):
    pass


class ConnectionTimeoutException(Exception):
    pass


class ConnectionRefusedException(Exception):
    pass


class NoRouteException(Exception):
    pass


class ConnectionClosedByRemoteHostException(Exception):
    pass


class ConnectionClosedException(Exception):
    pass


class ConnectionResetByPeerException(Exception):
    pass


def _sendPassword(command, ip, password, timeout=30):
    """
        发送密码
    """
    child = pexpect.spawn(command, timeout=timeout)

    yesnoflag = 0

    ############################################################################
    # expect 1
    try:
        i = child.expect ([
            pexpect.TIMEOUT,
            'assword:',
            'yes/no',
            'FATAL',
            'No route to host',
            'Connection Refused',
            'Connection refused',
            'Host key verification failed',
            'Illegal host key',
            'Connection Timed Out',
            'Connection timed out',
            'Interrupted system call',
            'Connection closed by remote host',
            'Connection closed',
            'Connection reset by peer',
        ], timeout=timeout)
    except pexpect.EOF as e:
        # rsync可以没有密码
        # from binascii import hexlify
        # print("before1=", child.before)
        # print("before2=", hexlify(child.before))
        result = child.before
        if result == "\r\n" or not child.before:
            child.close()
            return result
        else:
            child.close()
            raise Exception(e)
            return False
    if i == 0:  # Timeout or EOF
        child.close()
        raise ExpectTimeoutException("CONNECTERROR: %(ip)s expect timeout!!!" % {'ip': ip})
        return False
    if i == 1:  # 'assword:'
        child.sendline(password)
    if i == 2:  # 'yes/no)?'
        yesnoflag = 1
        child.sendline("yes")
    if i == 3:  # 'FATAL'
        child.close()
        raise Exception("CONNECTERROR: %(ip)s occur FATAL ERROR!!!" % {'ip': ip})
        return False
    if i == 4:  # 'No route to host'
        child.close()
        raise NoRouteException("CONNECTERROR: %(ip)s No route to host!!!" % {'ip': ip})
        return False
    if i == 5:  # 'Connection Refused'
        child.close()
        raise ConnectionRefusedException("CONNECTERROR: %(ip)s Connection Refused!!!" % {'ip': ip})
        return False
    if i == 6:  # Connection refused
        child.close()
        raise ConnectionRefusedException("CONNECTERROR: %(ip)s Connection refused!!!" % {'ip': ip})
        return False
    if i == 7:  # Host key verification failed
        child.close()
        raise Exception("CONNECTERROR: %(ip)s Host key verification failed!!!" % {'ip': ip})
        return False
    if i == 8:  # Illegal host key
        child.close()
        raise Exception("CONNECTERROR: %(ip)s Illegal host key!!!" % {'ip': ip})
        return False
    if i == 9:  # Connection Timed Out
        child.close()
        raise ConnectionTimeoutException("CONNECTERROR: %(ip)s login TIMEOUT!!!" % {'ip': ip})
        return False
    if i == 10:  # Connection timed out
        child.close()
        raise ConnectionTimeoutException("CONNECTERROR: %(ip)s login TIMEOUT!!!" % {'ip': ip})
        return False
    if i == 11:  # Interrupted system call
        child.close()
        raise Exception("%(ip)s Interrupted system call!!!" % {'ip': ip})
    if i == 12:  # Connection closed by remote host
        child.close()
        raise ConnectionClosedByRemoteHostException("%(ip)s Connection closed by remote host!!!" % {'ip': ip})
    if i == 13:  # Connection closed
        child.close()
        raise ConnectionClosedException("%(ip)s Connection closed!!!" % {'ip': ip})
    if i == 14:  # Connection reset by peer
        child.close()
        raise ConnectionResetByPeerException("%(ip)s Connection reset by peer!!!" % {'ip': ip})

    ############################################################################
    # expect 2
    if yesnoflag == 1:
        i = child.expect ([
                'assword:',
                'yes/no',
            ])
        if i == 0:
            child.sendline(password)
        if i == 1:
            yesnoflag = 2
            child.sendline("yes")

    ############################################################################
    # expect 3
    if yesnoflag == 2:
        i = child.expect ([
                'assword:',
            ])
        if i == 0:
            child.sendline(password)

    ############################################################################
    # expect 4
    i = child.expect ([
            'assword:',
            'authentication',
            'no such file',
            'No such file or directory',
            'unspecified failure',
            'rsync error',
            'permission denied',
            'FATAL',
            pexpect.TIMEOUT,
            pexpect.EOF
        ])
    if i == 0:
        child.sendline(password)
        child.close()
        errmessage = "%s %s" % (child.before.strip(), child.after)
        raise PasswordException("password error: %(ip)s %(errmessage)s!!!" % {'ip': ip, 'errmessage': errmessage})
    elif i == 1:
        child.sendline(password)
        child.close()
        errmessage = "%s %s" % (child.before.strip(), child.after)
        raise PasswordException("password error: %(ip)s %(errmessage)s!!!" % {'ip': ip, 'errmessage': errmessage})
    elif i == 2:
        child.close()
        errmessage = "%s %s" % (child.before.strip(), child.after)
        raise ScpNoSuchFileException("no such file: %(ip)s %(errmessage)s!!!" % {'ip': ip, 'errmessage': errmessage})
    elif i == 3:
        child.close()
        errmessage = "%s %s" % (child.before.strip(), child.after)
        raise ScpNoSuchFileException("No such file or directory: %(ip)s %(errmessage)s!!!" % {'ip': ip, 'errmessage': errmessage})
    elif i == 4:
        child.close()
        errmessage = "%s %s" % (child.before.strip(), child.after)
        raise Exception("unspecified failure: %(ip)s %(errmessage)s!!!" % {'ip': ip, 'errmessage': errmessage})
    elif i == 5:
        child.close()
        errmessage = "%s %s" % (child.before.strip(), child.after)
        raise Exception("rsync error: %(ip)s %(errmessage)s!!!" % {'ip': ip, 'errmessage': errmessage})
    elif i == 6:
        child.close()
        errmessage = "%s %s" % (child.before.strip(), child.after)
        raise Exception("permission denied: %(ip)s %(errmessage)s!!!" % {'ip': ip, 'errmessage': errmessage})
    elif i == 7:
        child.close()
        errmessage = "%s %s" % (child.before.strip(), child.after)
        raise Exception("FATAL ERROR: %(ip)s %(errmessage)s!!!" % {'ip': ip, 'errmessage': errmessage})
    elif i == 8:
        child.close()
        errmessage = "%s %s" % (child.before.strip(), child.after)
        raise ExpectTimeoutException("TIMEOUT: %(ip)s %(errmessage)s!!!" % {'ip': ip, 'errmessage': errmessage})
    elif i == 9:
        # print("ABS_OK_SCP: %(ip)s" %{'ip': ip})
        result = child.before
        child.close()
        return result
    result = child.before
    child.close()
    return result


sendPassword = _sendPassword


def scpUsage():
    print("")
    print("### USAGE:  scp ip user passwd port sourcefile destdir direction bwlimit timeout")
    print("")
    print("            sourcefile: a file or directory to be transferred")
    print("                        需要拷贝目录时目录名后不要带/，否则会拷贝该目录下的所有文件")
    print("            destdir:    the location that the sourcefile to be put into")
    print("            direction:  pull or push.")
    print("                        pull: remote -> local")
    print("                        push: local -> remote")
    print("            bwlimit:    bandwidth limit, kbit/s, 0 means no limit")
    print("            timeout:    timeout of expect, s, -1 means no timeout")
    print("")


def getScpPath():
    for pathname in [
        "/usr/bin/scp",
        "/usr/local/bin/scp2",
        "/usr/bin/scp.exe",
    ]:
        if os.path.exists(pathname):
            return pathname
    return None


def getSshPath():
    for pathname in [
        "/usr/bin/ssh",
        "/usr/local/bin/ssh2",
        "/usr/bin/ssh.exe",
    ]:
        if os.path.exists(pathname):
            return pathname
    return None


def getRsyncPath():
    for pathname in [
        "/usr/bin/rsync",
        "/usr/local/bin/rsync",
        "/usr/bin/rsync.exe",
    ]:
        if os.path.exists(pathname):
            return pathname
    return None


def scp(ip, user, password, port, sourcefile, destdir, direction, bwlimit=0, timeout= -1, type=1):
    """
    # select scp tool IN  /usr/local/bin/scp2 /usr/bin/scp /usr/bin/scp.exe
    # OS : ssh2 (suse10) , openssh (suse11/cygwin/centos)
    # add rsync timeout 15 seconds
    # set default ssh  /usr/bin/ssh
    # add connect timeout 30 seconds
    # add rsync path:/usr/local/bin/rsync , for slackware 8.1

    # scp2: -p Tells scp2 to preserve file attributes and timestamps
    # scp2: -r Copy directories recursively.  Does not follow symbolic links
    # scp2: -Q Do not show process indicator

    # rsync: -a, --archive, archive mode, equivalent to -rlptgoD
    # rsync: -r, --recursive, recurse into directories
    # rsync: -t, --times, preserve times
    # rsync: -z, --compress, compress file data
    # rsync: --progress show progress during transfer


        通过scp / rsync上传，下载文件
        sourcefile: a file or directory to be transferred"
                    需要拷贝目录时目录名后不要带/，否则会拷贝该目录下的所有文件
        destdir:    the location that the sourcefile to be put into"
        direction:  pull or push."
            pull: remote -> local"
            push: local -> remote"
        bwlimit:    bandwidth limit, kbit/s, 0 means no limit"
        timeout:    timeout of expect, s, -1 means no timeout"

        scp2: -p Tells scp2 to preserve file attributes and timestamps
        scp2: -r Copy directories recursively.  Does not follow symbolic links
        scp2: -Q Do not show process indicator

        rsync: -a, --archive, archive mode, equivalent to -rlptgoD
        rsync: -r, --recursive, recurse into directories
        rsync: -t, --times, preserve times
        rsync: -z, --compress, compress file data
        rsync: --progress show progress during transfer

        ps: 需要拷贝目录时目录名后不要带/，否则会拷贝该目录下的所有文件

        from misc import scp

        TGP
        a = ['10.194.148.42', '', '', '8730', 'flow_log/*.2014120213', '/data/icaccount/logfile/10.194.148.42/30230191/58', 'pull', 1000, -1, 2]
        scp(*a)

        业务安全
        b = ['10.166.135.80', 'ds_dz', 'ds_DZ@42', '36000', '/data/flow_log/*.2014120213', '/data/icaccount/logfile/10.166.135.80/30230184/55', 'pull', 1000, -1, 1]
        scp(*a)

        微信商城
        c = ['10.208.154.46', '', '', '873', 'idip/*.2014120309', '/data/icaccount/logfile/10.208.154.46/30301393/54', 'pull', 1000, -1, 2]
        scp(*c)

    """
    scp = getScpPath()
    ssh = getSshPath()
    rsync = getRsyncPath()
    commandStr = ''
    if direction == "pull":
        if bwlimit > 0:
            if type == 1:
                commandStr = "%(rsync)s -artz --bwlimit=%(bwlimit)s -e '%(ssh)s -l%(user)s -p%(port)s' %(ip)s:%(sourcefile)s %(destdir)s" % {
                    'rsync': rsync,
                    'bwlimit': bwlimit,
                    'ssh': ssh,
                    'user': user,
                    'port': port,
                    'ip': ip,
                    'sourcefile': sourcefile,
                    'destdir': destdir,
                }
            elif type == 2:
                if not user:
                    commandStr = "%(rsync)s -artRz --bwlimit=%(bwlimit)s --port=%(port)s %(ip)s::%(sourcefile)s %(destdir)s"
                else:
                    commandStr = "%(rsync)s -artRz --bwlimit=%(bwlimit)s --port=%(port)s %(user)s@%(ip)s::%(sourcefile)s %(destdir)s"
                commandStr = commandStr % {
                    'rsync': rsync,
                    'bwlimit': bwlimit,
                    'port': port,
                    'user': user,
                    'ip': ip,
                    'sourcefile': sourcefile,
                    'destdir': destdir,
                }
            elif type == 3:
                if not user:
                    commandStr = "%(rsync)s rsync://%(ip)s:%(port)s%(sourcefile)s %(destdir)s" % {
                        'rsync': rsync,
                        'port': port,
                        'ip': ip,
                        'sourcefile': sourcefile,
                        'destdir': destdir,
                    }
        elif bwlimit == 0:
            commandStr = "%(scp)s -r -p -P %(port)s %(user)s@%(ip)s:%(sourcefile)s %(destdir)s" % {
                'scp': scp,
                'user': user,
                'ip': ip,
                'port': port,
                'sourcefile': sourcefile,
                'destdir': destdir,
            }
        else:
            scpUsage()
            return
    elif direction == "push":
        if bwlimit > 0:
            commandStr = "%(rsync)s -avrtz --bwlimit=%(bwlimit)s -e '%(ssh)s -l%(user)s -p%(port)s' %(sourcefile)s %(ip)s:%(destdir)s" % {
                'rsync': rsync,
                'ssh': ssh,
                'bwlimit': bwlimit,
                'user': user,
                'port': port,
                'sourcefile': sourcefile,
                'ip': ip,
                'destdir': destdir,
            }
        elif bwlimit == 0:
            commandStr = "%(scp)s -r -p -P %(port)s %(sourcefile)s %(user)s@%(ip)s:%(destdir)s" % {
                'scp': scp,
                'sourcefile': sourcefile,
                'user': user,
                'ip': ip,
                'port': port,
                'destdir': destdir,
            }
        else:
            scpUsage()
            return
    else:
        scpUsage()
        return

    # 发送密码
    if commandStr:
        return _sendPassword(commandStr, ip, password)


def runRemoteCommand(ip, username, password, port, sCommand, timeout=60):
    """
        执行远程系统命令
    """
    ssh = getSshPath()
    command_str = "%s -p %s -l%s %s %s" % (ssh, str(port), username, ip, sCommand)
    if command_str:
        return _sendPassword(command_str, ip, password, timeout)
    return None


def dumpGarbage():
    import gc
    gc.enable()
    _unreachable = gc.collect()
    print('unreachable object num:%d' % _unreachable)
    print('garbage object num:%d' % len(gc.garbage))

    print("gc.garbage = ", gc.garbage)
    for obj in gc.garbage:
        print(obj.__dict__)


def listData(rows, key, value):
    """
        将两个字段转换为词典格式
    """
    result = {}
    for row in rows:
        result[row[key]] = row[value]
    return result


def getIp(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def get_local_host_ip(ifname='eth1'):
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


def printStats(filename='.profile', sortField='time'):
    """
        显示性能剖析文件
    """
    import pstats
    p = pstats.Stats(filename)
    p.sort_stats(sortField).print_stats()


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


def ustr2unicode(unicodeStr, sep='\\'):
    """
        将以反斜杠分割的unicode格式字符串格式化为unicode
        '\u56c3\u67e4' 转 u'\u56c3\u67e4'
        @param sep: 原字符串的分隔符
        a = "%u67E5%u8BE2%u5DE5%u4F1A%u4FE1%u606F%u63A5%u53E3"
        print ustr2unicode(a, '%').encode('gbk')
    """
    if sep != '\\':
        unicodeStr = unicodeStr.replace(sep, '\\')
    return "".join(unichr(int(c, 16)) for c in unicodeStr.split(r"\u")[1:])


def format_time(seconds):
    """Formats time as the string "HH:MM:SS".
        In [10]: str(datetime.timedelta(seconds=int(10)))
        Out[10]: '0:00:10'
    """
    return str(datetime.timedelta(seconds=int(seconds)))


def isMemoryAvailable(limit=80):
    """ 检查内存空间是否可用 """
    virtualMemory = psutil.virtual_memory()
    percent = virtualMemory.percent
    if percent > limit:
        return False
    return True


def isDiskAvailable(dirname, limit=80):
    """ 检查磁盘空间是否可用 """
    diskUsage = psutil.disk_usage(dirname)
    percent = diskUsage.percent
    if percent > limit:
        return False
    return True


def getColCount(row):
    """ 获得文本列数 """
    lines = re.split("\s", row)
    return len([i for i in lines if i])


def formatRow(row):
    """ 日志行按空白字符分隔 """
    lines = re.split("\s", row.strip())
    return [i for i in lines if i]


def getFileRowColCount(filePath):
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
                if row == 1:
                    col = getColCount(line)
    return (row, col)


def getFileRow(filePath):
    """获得文件行数 ."""
    with open(filePath, 'r') as rFb:
        return sum(1 for row in rFb if row)


if PY2:
    from itertools import izip_longest as zip_longest  # for Python 2.x
else:
    from itertools import zip_longest # for Python 3.x
# from six.moves import zip_longest # for both (uses the six compat library)


def grouper(n, iterable, padvalue=None):
    """grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"""
    return zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)


def chunksWithPad(input, size):
    return map(None, *([iter(input)] * size))


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


def formatSqlSelectResult(data):
    """格式化select sql语句的结果 ."""
    dataList = data.split('\n')
    res = []
    for row in dataList:
        if not row:
            continue
        if row.startswith("+-"):
            continue
        row = [item.strip() for item in row.split('|') if item.strip()]
        res.append(row)
    return res


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


def initLogger(log_path, name=""):
    """初始化日志 ."""
    log_dir = os.path.basename(log_path)
    if not os.path.exists(log_dir):
        try:
            os.mkdir(log_dir)
        except Exception:
            log_dir = "."
    logger = logging.getLogger(name)
    filehandler = TimedRotatingFileHandler(log_path, 'MIDNIGHT', 1, 14)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    filehandler.setFormatter(formatter)
    # filehandler.suffix = "%Y%m%d.log"
    logger.addHandler(filehandler)
    logger.setLevel(logging.DEBUG)
    return logger


def init_logger_with_timed_rotaing(log_path, when='MIDNIGHT',
                                   interval=1,
                                   backupCount=14):
    """初始化日志 ."""
    logger = logging.getLogger()
    filehandler = TimedRotatingFileHandler(log_path, when, interval, backupCount)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    filehandler.setFormatter(formatter)
    #filehandler.suffix = "%Y%m%d.log"
    logger.addHandler(filehandler)
    logger.setLevel(logging.INFO)
    return logger


class DatetimeEncoder(json.JSONEncoder):
    """JSON转换器

    Examples:
        json.dumps(dictionary, cls=DatetimeEncoder)
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')

        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)

        return json.JSONEncoder.default(self, obj)


def parseDbConfig(dbConfig):
    """用于将db配置转换成torndb可识别的参数格式 ."""
    host = dbConfig.get('host')
    user = dbConfig.get('user')
    password = dbConfig.get('password')
    if not password:
        password = dbConfig.get('passwd')
    charset = dbConfig.get('charset')
    database = dbConfig.get('database')
    if not database:
        database = dbConfig.get('db')
    return (host, database, user, password, 7 * 3600, 0, "+0:00", charset)


def ipv4_into_int(ip):
    # 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“.”后转成10进制的 3232235789 即可。
    # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    return reduce(lambda x,y:(x<<8)+y,map(int,ip.split('.')))


def is_internal_ipv4(ip):
    """内网IPV4地址判断 ."""
    ip = ipv4_into_int(ip)
    net_a = ipv4_into_int('10.255.255.255') >> 24
    net_b = ipv4_into_int('172.31.255.255') >> 20
    net_c = ipv4_into_int('192.168.255.255') >> 16
    return ip >> 24 == net_a or ip >>20 == net_b or ip >> 16 == net_c


def tob(s, enc='utf-8'):
    """将字符串转换为utf8/bytes编码 ."""
    return s.encode(enc) if not isinstance(s, bytes) else s


def tou(s, enc='utf-8'):
    """将字符串转换为unicode编码 ."""
    return s.decode(enc) if isinstance(s, bytes) else s


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
