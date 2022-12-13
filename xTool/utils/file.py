# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import errno
import os
import re
import shutil
import zipfile
from contextlib import contextmanager
from io import StringIO
from tempfile import mkdtemp, NamedTemporaryFile

from xTool.exceptions import XToolConfigException
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


def write_temp_file(content, mode='w+b', buffering=-1, encoding=None,
                    newline=None, suffix=None, prefix=None,
                    dir=None, delete=True):
    """写临时文件 ."""
    with NamedTemporaryFile(mode, buffering, encoding,
                            newline, suffix, prefix,
                            dir, delete) as writer:
        writer.write(content)
        return writer.name


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


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise XToolConfigException(
                'Error creating {}: {}'.format(path, exc.strerror))


def list_py_file_paths(
    directory,
    followlinks=True,
    ignore_filename='.ignore',
    file_ext='.py',
    safe_mode=False,
    safe_filters=(b'xTool', b'XTool')):
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
        patterns_by_dir = {}
        # 递归遍历目录，包含链接文件
        for root, dirs, files in os.walk(directory, followlinks=followlinks):
            patterns = patterns_by_dir.get(root, [])
            # 获得需要忽略的文件
            ignore_file = os.path.join(root, ignore_filename)
            if os.path.isfile(ignore_file):
                with open(ignore_file, 'r') as f:
                    # If we have new patterns create a copy so we don't change
                    # the previous list (which would affect other subdirs)
                    patterns = patterns + \
                               [p for p in f.read().split('\n') if p]

            # If we can ignore any subdirs entirely we should - fewer paths
            # to walk is better. We have to modify the ``dirs`` array in
            # place for this to affect os.walk
            dirs[:] = [
                d
                for d in dirs
                if not any(re.search(p, os.path.join(root, d)) for p in patterns)
            ]

            # We want patterns defined in a parent folder's .airflowignore to
            # apply to subdirs too
            for d in dirs:
                patterns_by_dir[os.path.join(root, d)] = patterns

            for f in files:
                try:
                    # 获得文件的绝对路径
                    file_path = os.path.join(root, f)
                    if not os.path.isfile(file_path):
                        continue
                    # 验证文件后缀
                    mod_name, file_extension = os.path.splitext(
                        os.path.split(file_path)[-1])
                    if file_extension != file_ext and not zipfile.is_zipfile(
                        file_path):
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


class DiskWalk:
    """API for getting directory walking collections"""

    def __init__(self, path: str):
        self.path = path

    def enumerate_file_paths(self):
        """Returns the path to all the files in a directory as a list"""
        for dir_path, _, filenames in os.walk(self.path):
            for file in filenames:
                full_path = os.path.join(dir_path, file)
                yield full_path

    def enumerate_dir_paths(self):
        """Returns all the directories in a directory as a list"""
        for dir_path, dir_names, _ in os.walk(self.path):
            for dirname in dir_names:
                full_path = os.path.join(dir_path, dirname)
                yield full_path


def get_unzipped_files(package):
    """
    解压zip文件，获取文件列表
    """
    input_zip = zipfile.ZipFile(package)
    return {name: StringIO(input_zip.read(name)) for name in input_zip.namelist()}
