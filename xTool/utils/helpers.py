import os
import platform
import re
import shlex
import subprocess
import sys
from builtins import input
from datetime import datetime
from functools import reduce

from jinja2 import Template

from xTool.exceptions import XToolException


def validate_key(k, max_length=250):
    """验证key的格式 ."""
    if not isinstance(k, str):
        raise TypeError("The key has to be a string")
    elif len(k) > max_length:
        raise XToolException("The key has to be less than {0} characters".format(max_length))
    elif not re.match(r"^[A-Za-z0-9_\-\.]+$", k):
        raise XToolException(
            "The key ({k}) has to be made of alphanumeric characters, dashes, "
            "dots and underscores exclusively".format(**locals())
        )
    else:
        return True


def alchemy_to_dict(obj):
    """将SQLAlchemy model instance转化为字典，
    并将时间格式化为iso格式的字符串
    Transforms a SQLAlchemy model instance into a dictionary
    """
    if not obj:
        return None
    d = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.name)
        # 格式化时间
        if isinstance(value, datetime):
            value = value.isoformat()
        d[c.name] = value
    return d


def ask_yesno(question):
    yes = set(["yes", "y"])
    no = set(["no", "n"])

    done = False
    print(question)
    while not done:
        choice = input().lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond by yes or no.")


def strtobool(val):
    """
    This function was borrowed from distutils.utils. While distutils
    is part of stdlib, it feels odd to use distutils in main application code.

    The function was modified to walk its talk and actually return bool
    and not int.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def is_in(obj, l):
    """判断obj对象是否在l中，判断相等的逻辑是is，而不是=
    Checks whether an object is one of the item in the list.
    This is different from ``in`` because ``in`` uses __cmp__ when
    present. Here we change based on the object itself
    """
    for item in l:
        if item is obj:
            return True
    return False


def is_container(obj):
    """判断对象是否可以遍历，但不是字符串
    Test if an object is a container (iterable) but not a string
    """
    return hasattr(obj, "__iter__") and not isinstance(obj, str)


def as_tuple(obj):
    """将可遍历对象转换为元组，将无法遍历的元素转换为只有一个的元组
    If obj is a container, returns obj as a tuple.
    Otherwise, returns a tuple containing obj.
    """
    if is_container(obj):
        return tuple(obj)
    else:
        return tuple([obj])


def chunks(items, chunk_size):
    """将数组按指定大小分割
    Yield successive chunks of a given size from a list of items
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be a positive integer")
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def reduce_in_chunks(fn, iterable, initializer, chunk_size=0):
    """将数组 iterable 分组后，并对分片进行fn计算
    Reduce the given list of items by splitting it into chunks
    of the given size and passing each chunk through the reducer
    """
    if len(iterable) == 0:
        return initializer
    if chunk_size == 0:
        chunk_size = len(iterable)
    return reduce(fn, chunks(iterable, chunk_size), initializer)


def as_flattened_list(iterable):
    """将二维数组展开为一维数组
    Return an iterable with one level flattened

    >>> as_flattened_list((('blue', 'red'), ('green', 'yellow', 'pink')))
    ['blue', 'red', 'green', 'yellow', 'pink']

    等价于
    list(itertools.chain.from_iterable((('blue', 'red'), ('green', 'yellow', 'pink'))))
    """
    return [e for i in iterable for e in i]


def chain(*tasks):
    """将任务连成线
    Given a number of tasks, builds a dependency chain.

    chain(task_1, task_2, task_3, task_4)

    is equivalent to

    task_1.set_downstream(task_2)
    task_2.set_downstream(task_3)
    task_3.set_downstream(task_4)
    """
    for up_task, down_task in zip(tasks[:-1], tasks[1:]):
        up_task.set_downstream(down_task)


def pprinttable(rows):
    """打印一个漂亮的ascii表格
        Returns a pretty ascii table from tuples

    If namedtuple are used, the table will have headers
    """
    if not rows:
        return

    # 获得表格的头部
    if hasattr(rows[0], "_fields"):  # if namedtuple
        headers = rows[0]._fields
    else:
        headers = ["col{}".format(i) for i in range(len(rows[0]))]

    # 获得表头每一列的长度
    lens = [len(s) for s in headers]
    # 计算所有行中每一列的最大长度
    for row in rows:
        for i in range(len(rows[0])):
            slenght = len("{}".format(row[i]))
            if slenght > lens[i]:
                lens[i] = slenght

    # 获得行列格式
    formats = []
    hformats = []
    for i in range(len(rows[0])):
        if isinstance(rows[0][i], int):
            formats.append("%%%dd" % lens[i])
        else:
            formats.append("%%-%ds" % lens[i])
        hformats.append("%%-%ds" % lens[i])
    pattern = " | ".join(formats)
    hpattern = " | ".join(hformats)
    # 获得每一行的分隔符
    separator = "-+-".join(["-" * n for n in lens])
    s = ""
    s += separator + "\n"
    s += (hpattern % tuple(headers)) + "\n"
    s += separator + "\n"

    def f(t):
        return "{}".format(t) if isinstance(t, str) else t

    for line in rows:
        s += pattern % tuple(f(t) for t in line) + "\n"
    s += separator + "\n"
    return s


def parse_template_string(template_string):
    if "{{" in template_string:  # jinja mode
        return None, Template(template_string)
    else:
        return template_string, None


def expand_env_var(env_var):
    """使用环境变量替换env_var

    - 根据环境变量替换env_var
    - 把env_var中包含的”~”和”~user”转换成用户目录
    """
    if not env_var:
        return env_var
    while True:
        # 把env_var中包含的”~”和”~user”转换成用户目录
        # os.path.expandvars: 返回参数，其中的环境变量被扩展。参数中形如$name或者${name}的部分被替换成环境变量name的值。如果格式不正确或者引用了不存在的变量，则不进行替换（或者扩展）。
        #                     在Windows上, 除了$name和${name}之外还支持如%name%这样的扩展。
        interpolated = os.path.expanduser(os.path.expandvars(str(env_var)))
        # 如果相等则说明已经全部替换成功
        if interpolated == env_var:
            return interpolated
        else:
            # 如果不相等需要继续替换
            env_var = interpolated


def run_command(command):
    """执行shell命令，返回标准输出（Unicode编码） ."""
    if platform.system() == "Windows":
        close_fds = False
    else:
        close_fds = True
    process = subprocess.Popen(
        shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, close_fds=close_fds
    )
    # 将结果转换为unicode编码
    output, stderr = [stream.decode(sys.getdefaultencoding(), "ignore") for stream in process.communicate()]

    if process.returncode != 0:
        raise XToolException(
            "Cannot execute {}. Error code is: {}. Output: {}, Stderr: {}".format(
                command, process.returncode, output, stderr
            )
        )
    # 返回unicode编码的标准输出
    return output
