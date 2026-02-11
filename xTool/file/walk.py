import os


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


def walk_path(path: str, depth=float('inf'), follow_links=False):
    """This utility function returns a list directories suitable for use as the
    *searchpath* argument to :class:`PluginSource`. This will recursively add
    directories up to the specified depth.

    :param str path: The directory on the file system to start the search path
                     at. It will be included in the result.
    :param int depth: The number of directories to recurse into while building
                      the search path. By default the function will iterate into
                      all child directories.
    :param bool follow_links: Whether or not to recurse into directories which
                             are symbolic links.
    :return: A list of directories, including *path* and child directories.
    :rtype: list
    """
    # os.walk implements a depth-first approach which results in unnecessarily
    # slow execution when *path* is a large tree and *depth* is a small number
    paths = [path]
    # 列出指定目录下的所有文件和子目录
    for dir_entry in os.listdir(path):
        # 只处理目录
        sub_path = os.path.join(path, dir_entry)
        if not os.path.isdir(sub_path):
            continue
        # 忽略链接
        if not follow_links and os.path.islink(sub_path):
            continue
        # 递归查询子目录
        if depth:
            paths.extend(walk_path(sub_path, depth - 1, follow_links))

    return paths


def filter_directory_files(directory: str, exts: list[str]) -> dict[str, str]:
    """根据后缀过滤文件"""
    result: dict[str, str] = {}
    accept: list[str] = [name.lower() for name in exts]

    for song in os.listdir(directory):
        name, ext = os.path.splitext(song)
        if ext.lower() in accept:
            result[name] = os.path.join(directory, song)

    return result
