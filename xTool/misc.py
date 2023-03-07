# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import base64
import collections
import decimal
import hashlib
import inspect
import io
import itertools
import json
import os
import platform
import random
import re
import subprocess
import sys
import traceback
import warnings
from datetime import datetime, date
from io import StringIO
from typing import List, Iterable, Union, Dict

try:
    import numpy as np
except ImportError:
    np = None

import psutil
from asyncio.constants import DEBUG_STACK_DEPTH

from xTool.compat import basestring

# Determine platform being used.
system = platform.system()
USE_MAC = USE_WINDOWS = USE_LINUX = USE_CYGWIN = USE_X11 = False
if system == 'Darwin':
    USE_MAC = True
elif system == 'Windows' or system == 'Microsoft':
    USE_WINDOWS = True
elif system == "Linux":
    USE_LINUX = True
elif system.startswith("CYGWIN"):
    USE_CYGWIN = True
else:  # Default to X11
    USE_X11 = True
OS_IS_WINDOWS = os.name == "nt"

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3

if PY3:
    xrange = range
    izip_longest = itertools.zip_longest
else:
    izip_longest = itertools.izip_longest
zip_longest = izip_longest

sentinel = object()  # type: Any

CHAR = set(chr(i) for i in range(0, 128))
CTL = set(chr(i) for i in range(0, 32)) | {chr(127), }
SEPARATORS = {'(', ')', '<', '>', '@', ',', ';', ':', '\\', '"', '/', '[', ']',
              '?', '=', '{', '}', ' ', chr(9)}
# 按位异或
TOKEN = CHAR ^ CTL ^ SEPARATORS


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


def exception_to_string():
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
    return frame.f_code.co_name, frame.f_lineno


def run_command(command):
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


def get_run_command_result(command):
    proc = subprocess.Popen(command,
                            shell=True,
                            close_fds=False if USE_WINDOWS else False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    stdout_data, stderr_data = proc.communicate()
    return proc.returncode, stdout_data, stderr_data


def json_ser(obj):
    """json serializer that deals with dates.

    usage: json.dumps(object, default=utils.json.json_ser)
    """
    if isinstance(obj, (datetime, date)):
        # Return a string representing the date and time in ISO 8601 format,
        # YYYY-MM-DDTHH:MM:SS.mmmmmm or, if microsecond is 0,
        # YYYY-MM-DDTHH:MM:SS
        return obj.isoformat()


class NumpyJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        # convert dates and numpy objects in a json serializable format
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        if np:
            if type(obj) in (np.int_,
                             np.intc,
                             np.intp,
                             np.int8,
                             np.int16,
                             np.int32,
                             np.int64,
                             np.uint8,
                             np.uint16,
                             np.uint32,
                             np.uint64):
                return int(obj)
            elif type(obj) in (np.bool_,):
                return bool(obj)
            elif type(obj) in (np.float_,
                               np.float16,
                               np.float32,
                               np.float64,
                               np.complex_,
                               np.complex64,
                               np.complex128):
                return float(obj)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def is_memory_available(limit=80):
    """检查内存空间是否可用 """
    virtual_memory = psutil.virtual_memory()
    percent = virtual_memory.percent
    if percent > limit:
        return False
    return True


def is_disk_available(dirname, limit=80):
    """检查磁盘空间是否可用 """
    disk_usage = psutil.disk_usage(dirname)
    percent = disk_usage.percent
    if percent > limit:
        return False
    return True


def grouper(n, iterable, padvalue=None):
    """grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"""
    return zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)


def chunks(items, chunk_len):
    """Yield successive n-sized chunks from l."""
    return (items[i:i + chunk_len] for i in xrange(0, len(items), chunk_len))


def chunked(it, chunk_len):
    marker = object()
    for group in (list(g) for g in izip_longest(*[iter(it)] * chunk_len,
                                                fillvalue=marker)):
        if group[-1] is marker:
            del group[group.index(marker):]
        yield group


def chunk_list(iterable, size):
    iterable = iter(iterable)

    item = list(itertools.islice(iterable, size))
    while item:
        yield item
        item = list(itertools.islice(iterable, size))


def get_random_string(length=32,

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

        `code source <http://code.oa.com/v2/weima/detail/70493>`_
    """
    assert isinstance(data, basestring)

    dump_list = []
    slice_str = ""
    addr = 0

    for byte in data:
        if addr % 16 == 0:
            dump_list.append(" ")

            for char in slice_str:
                if 32 <= ord(char) <= 126:
                    dump_list.append(char)
                else:
                    dump_list.append(".")

            dump_list.append("\n%04x: " % addr)
            slice_str = ""

        dump_list.append("%02x " % ord(byte))
        slice_str += byte
        addr += 1

    remainder = addr % 16

    if remainder != 0:
        dump_list.append("   " * (16 - remainder) + " ")

    for char in slice_str:
        if 32 <= ord(char) <= 126:
            dump_list.append(char)
        else:
            dump_list.append(".")

    print("".join(dump_list))


def strict_bool(s):
    """
    Variant of bool() that only accepts two possible string values.
    """
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError(s)


def less_strict_bool(x):
    """
    Idempotent and None-safe version of strict_bool.
    """
    if x is None:
        return False
    elif x is True or x is False:
        return x
    else:
        return strict_bool(x)


def properties(obj):
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
    return dict((attr, getattr(obj, attr))
                for attr in dir(obj)
                if not attr.startswith('__'))


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


def __deprecated__(s):
    warnings.warn(s, DeprecationWarning)


# Helper functions that are used in various parts of the codebase.
MODEL_BASE = '_metaclass_helper_'


def with_metaclass(meta, base=object):
    """根据元类创建一个类 ."""
    return meta(MODEL_BASE, (base,), {})


def merge_dict(source, overrides):
    """字典合并，返回新的字典 ."""
    merged = source.copy()
    if overrides:
        merged.update(overrides)
    return merged


def quote(path, quote_chars):
    if len(path) == 1:
        return path[0].join(quote_chars)
    return '.'.join([part.join(quote_chars) for part in path])


def ensure_tuple(value):
    if value is not None:
        return value if isinstance(value, (list, tuple)) else (value,)


# Regular expressions used to convert class names to snake-case table names.
# First regex handles acronym followed by word or initial lower-word followed
# by a capitalized word. e.g. APIResponse -> API_Response / fooBar -> foo_Bar.
# Second regex handles the normal case of two title-cased words.
SNAKE_CASE_STEP1 = re.compile('(.)_*([A-Z][a-z]+)')
SNAKE_CASE_STEP2 = re.compile('([a-z0-9])_*([A-Z])')


def camel_to_snake(camel_str: str) -> str:
    """将驼峰命名转换为下划线方式的小写命名 ."""
    first = SNAKE_CASE_STEP1.sub(r'\1_\2', camel_str)
    return SNAKE_CASE_STEP2.sub(r'\1_\2', first).lower()


def camel_to_snake_2(camel_str: str) -> str:
    """将驼峰命名转换为下划线方式的小写命名 ."""
    buf = io.StringIO()
    str_len = len(camel_str)

    for i, cur_letter in enumerate(camel_str):
        if i and cur_letter == cur_letter.upper():
            prev_letter = camel_str[i - 1]
            next_letter = camel_str[i + 1] if i < str_len - 1 else "A"
            if cur_letter.isalpha():
                if prev_letter != prev_letter.upper() or next_letter != next_letter.upper():
                    buf.write("_")
        buf.write(cur_letter)

    result = buf.getvalue()
    buf.close()

    return result.lower()


def snake_to_camel(name: str, title_case=False) -> str:
    """将下划线命名改为驼峰命名 ."""
    items = name.split("_")
    first_item = items[0].title() if title_case else items[0]
    if len(items) == 1:
        return first_item
    other_items = [item.title() for item in items[1:]]
    camel_name = "{}{}".format(first_item, ''.join(other_items))
    return camel_name


def md5(src):
    if not src:
        return None
    m = hashlib.md5()
    m.update(tob(src))
    return m.hexdigest()


def file_md5sum(file):
    file.seek(0, 0)

    m = hashlib.md5()
    for chunk in file.chunks():
        m.update(chunk)

    file.seek(0, 0)
    return m.hexdigest()


def count_md5(content, dict_sort=True, list_sort=True):
    if dict_sort and isinstance(content, dict):
        content = [(str(k), count_md5(content[k], dict_sort, list_sort)) for k in sorted(content.keys())]
        return count_md5(content, dict_sort, list_sort)
    elif isinstance(content, (list, tuple)):
        content = (
            sorted([count_md5(k, dict_sort, list_sort=True) for k in content])
            if list_sort
            else [count_md5(k, dict_sort, list_sort) for k in content]
        )
        return md5(str(content))
    elif callable(content):
        return make_callable_hash(content)
    return md5(str(content))


def make_callable_hash(content):
    """
    计算callable的hash
    """
    if inspect.isclass(content):
        h = []
        for attr in [i for i in sorted(dir(content)) if not i.startswith("__")]:
            v = getattr(content, attr)
            h.append(count_md5(v))

        return md5("".join(h))
    try:
        return md5(content.__name__)
    except AttributeError:
        try:
            return md5(content.func.__name__)
        except AttributeError:
            return md5(str(content))


def get_md5(content):
    if isinstance(content, list):
        return [count_md5(c) for c in content]
    else:
        return count_md5(content)


def humanize(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


def is_iterable(obj):
    return isinstance(obj, collections.Iterable)


if hasattr(sys, "_getframe"):
    def get_current_frame():
        return sys._getframe(3)
else:  # pragma: no cover

    def get_current_frame():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back


def get_bool_env(name: str, default=None) -> bool:
    value = os.getenv(name, default)
    if not value:
        return False
    if value in ("False", "false", "0"):
        return False
    return True


def extract_stack(f=None, limit=None):
    """Replacement for traceback.extract_stack() that only does the
    necessary work for asyncio debug mode.

        来自python3.9 asyncio
    """
    if f is None:
        f = sys._getframe().f_back
    if limit is None:
        # Limit the amount of work to a reasonable amount, as extract_stack()
        # can be called for each coroutine and future in debug mode.
        limit = DEBUG_STACK_DEPTH
    stack = traceback.StackSummary.extract(traceback.walk_stack(f),
                                           limit=limit,
                                           lookup_lines=False)
    stack.reverse()
    return stack


class UseTimesGenerator:
    """获得每个对象的使用次数 ."""

    def __init__(self):
        self.cache = {}

    def __call__(self, obj: object):
        """获得自增ID，范围1 ～ 4294967295，线程不安全 ."""
        if obj not in self.cache:
            # 初始值为1
            value = 1
            self.cache[obj] = 1
        else:
            # 下一值自增
            old_value = self.cache[obj]
            value = (old_value + 1) & 0xffffffff
        self.cache[obj] = value
        return value


def flatten(items):
    """摊平表格 .

    Examples:
         [1, 2, [3, 4, [5, 6], 7], 8] -> 1 2 3 4 5 6 7 8
    """
    for x in items:
        if isinstance(x, collections.Iterable):
            yield from flatten(x)
        else:
            yield x


def unique_list(data: List):
    """将列表去重，保持原有顺序 . """
    return list(collections.OrderedDict.fromkeys(data))


def strip(obj):
    if isinstance(obj, dict):
        return {strip(key): strip(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [strip(item) for item in obj]
    elif isinstance(obj, str):
        return obj.strip()
    else:
        return obj


def convert_textarea_to_list(ips):
    return ips.replace("\r\n", "\n").split("\n")


def get_unique_list(value: Iterable) -> list:
    """list去重，并保持原有数据顺序 ."""
    return list(collections.OrderedDict.fromkeys(value))


def get_new_filename(file, new_file_name=None):
    new_file_name = new_file_name or file_md5sum(file)
    old_file_name = file.name
    # 获得文件后缀名
    ext = ""
    if "." in old_file_name:
        ext = old_file_name.split(".")[-1]

    if ext:
        new_file_name = "{}.{}".format(new_file_name, ext)
    return new_file_name


def tree():
    return collections.defaultdict(tree)


def convert_img_to_base64(image, format="PNG"):
    img_buffer = StringIO()
    image.save(img_buffer, format=format, quality=95)
    base64_value = base64.b64encode(img_buffer.getvalue())
    return "data:image/{format};base64,{value}".format(format=format.lower(), value=base64_value)


def safe_int(int_str, dft=0):
    try:
        int_val = int(int_str)
    except Exception:  # noqa
        try:
            int_val = int(float(int_str))
        except Exception:  # noqa
            int_val = dft
    return int_val


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return float("nan")


def proxy(obj):
    class Proxy:
        def __getattribute__(self, item):
            return getattr(obj, item)

    return Proxy()


# create a new context for this task
ctx = decimal.Context()

# 20 digits should be enough for everyone :D
ctx.prec = 20


def float_to_str(f):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    d1 = ctx.create_decimal(repr(f))
    return format(d1, "f")


def to_dict(obj):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in list(obj.items()):
            data[k] = to_dict(v)
        return data
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = {}
        for key in dir(obj):
            value = getattr(obj, key)
            if not key.startswith("_") and not callable(value):
                data[key] = to_dict(value)
        return data
    else:
        return obj


def camel_to_underscore(camel_str):
    assert isinstance(camel_str, str)

    buf = StringIO()
    str_len = len(camel_str)

    for i in range(str_len):
        cur_letter = camel_str[i]
        if i and cur_letter == cur_letter.upper():
            prev_letter = camel_str[i - 1]
            next_letter = camel_str[i + 1] if i < str_len - 1 else "A"
            if cur_letter.isalpha():
                if prev_letter != prev_letter.upper() or next_letter != next_letter.upper():
                    buf.write("_")
        buf.write(cur_letter)

    result = buf.getvalue()
    buf.close()

    return result.lower()


def camel_obj_key_to_underscore(obj: Union[List, Dict, str]) -> Union[List, Dict, str]:
    """将指定对象的key转换为下划线格式 ."""
    if isinstance(obj, str):
        return camel_to_snake_2(obj)
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            if isinstance(value, (list, dict)):
                value = camel_obj_key_to_underscore(value)
            if isinstance(key, str):
                new_obj[camel_to_snake_2(key)] = value
            else:
                new_obj[key] = value
        return new_obj
    new_obj = []
    if isinstance(obj, list):
        for value in obj:
            if isinstance(value, dict):
                value = camel_obj_key_to_underscore(value)
            new_obj.append(value)
            return new_obj
    return obj


def retry_once(action: callable):
    """重试一次 ."""
    try:
        action()
    except Exception:  # noqa
        try:
            action()
        except Exception as exc_info:  # noqa
            raise exc_info
