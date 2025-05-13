import os


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
