# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import errno
import os
import shutil
from tempfile import mkdtemp

from contextlib import contextmanager


import os
import re
import time
import zipfile
from abc import ABCMeta, abstractmethod
from collections import defaultdict

from xTool.utils.log.logging_mixin import LoggingMixin


@contextmanager
def TemporaryDirectory(suffix='', prefix=None, dir=None):
    """创建临时目录 .
    
    with TemporaryDirectory(prefix='xtool_tmp') as tmp_dir:
        pass
    """
    name = mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        yield name
    finally:
        try:
            shutil.rmtree(name)
        except OSError as e:
            # ENOENT - no such file or directory
            if e.errno != errno.ENOENT:
                raise e


def mkdirs(path, mode):
    """创建目录
    Creates the directory specified by path, creating intermediate directories
    as necessary. If directory already exists, this is a no-op.

    :param path: The directory to create
    :type path: str
    :param mode: The mode to give to the directory e.g. 0o755, ignores umask
    :type mode: int
    """
    try:
        o_umask = os.umask(0)
        os.makedirs(path, mode)
    except OSError:
        if not os.path.isdir(path):
            raise
    finally:
        os.umask(o_umask)


def list_py_file_paths(directory, followlinks=True, ignore_filename='.ignore', file_ext='.py', safe_mode=False, safe_filters=(b'xTool', b'XTool')):
    """递归遍历目录，返回匹配规则的文件列表
    Traverse a directory and look for Python files.

    :param directory: the directory to traverse
    :type directory: unicode
    :param safe_mode: whether to use a heuristic to determine whether a file
    contains Airflow DAG definitions
    :return: a list of paths to Python files in the specified directory
    :rtype: list[unicode]
    """
    file_paths = []
    if directory is None:
        return []
    elif os.path.isfile(directory):
        return [directory]
    elif os.path.isdir(directory):
        patterns = []
        # 递归遍历目录，包含链接文件
        for root, dirs, files in os.walk(directory, followlinks=followlinks):
            # 获得需要忽略的文件
            ignore_file = [f for f in files if f == ignore_filename]
            if ignore_file:
                f = open(os.path.join(root, ignore_file[0]), 'r')
                patterns += [p.strip() for p in f.read().split('\n') if p]
                f.close()
            for f in files:
                try:
                    # 获得文件的绝对路径
                    file_path = os.path.join(root, f)
                    if not os.path.isfile(file_path):
                        continue
                    # 验证文件后缀
                    mod_name, file_extension = os.path.splitext(
                        os.path.split(file_path)[-1])
                    if file_extension != file_ext and not zipfile.is_zipfile(file_path):
                        continue
                    # 验证忽略规则
                    if any([re.findall(p, file_path) for p in patterns]):
                        continue

                    # 使用启发式方式猜测是否是一个DAG文件，DAG文件需要包含DAG 或 airflow
                    # Heuristic that guesses whether a Python file contains an
                    # Airflow DAG definition.
                    might_contain_dag = True
                    if safe_mode and not zipfile.is_zipfile(file_path):
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            might_contain_dag = all(
                                [s in content for s in safe_filters])

                    if not might_contain_dag:
                        continue

                    file_paths.append(file_path)
                except Exception:
                    log = LoggingMixin().log
                    log.exception("Error while examining %s", f)
    return file_paths
