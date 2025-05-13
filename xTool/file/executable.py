import os

from xTool.strings import encoding as encoding_util
from xTool.system import platforms


def get_system_path():
    """Returns properly encoded system PATH variable string."""
    return encoding_util.GetEncodedValue(os.environ, "PATH")


def _find_executable_on_path(executable, path, pathext):
    """Internal function to a find an executable.

    Args:
      executable: The name of the executable to find.
      path: A list of directories to search separated by 'os.pathsep'.
      pathext: An iterable of file name extensions to use.

    Returns:
      str, the path to a file on `path` with name `executable` + `p` for
        `p` in `pathext`.

    Raises:
      ValueError: invalid input.
    """

    if isinstance(pathext, str):
        raise ValueError(
            "_find_executable_on_path(..., pathext='{}') failed "
            "because pathext must be an iterable of strings, but got "
            "a string.".format(pathext)
        )

    # Prioritize preferred extension over earlier in path.
    for ext in pathext:
        for directory in path.split(os.pathsep):
            # Windows can have paths quoted.
            directory = directory.strip('"')
            full = os.path.normpath(os.path.join(directory, executable) + ext)
            # On Windows os.access(full, os.X_OK) is always True.
            if os.path.isfile(full) and os.access(full, os.X_OK):
                return full
    return None


def _platform_executable_extensions(platform):
    if platform == platforms.OperatingSystem.WINDOWS:
        return (".exe", ".cmd", ".bat", ".com", ".ps1")
    else:
        return ("", ".sh")


def find_executable_on_path(executable, path=None, pathext=None, allow_extensions=False):
    """Searches for `executable` in the directories listed in `path` or $PATH.

    Executable must not contain a directory or an extension.

    Args:
      executable: The name of the executable to find.
      path: A list of directories to search separated by 'os.pathsep'.  If None
        then the system PATH is used.
      pathext: An iterable of file name extensions to use.  If None then
        platform specific extensions are used.
      allow_extensions: A boolean flag indicating whether extensions in the
        executable are allowed.

    Returns:
      The path of 'executable' (possibly with a platform-specific extension) if
      found and executable, None if not found.

    Raises:
      ValueError: if executable has a path or an extension, and extensions are
        not allowed, or if there's an internal error.
    """

    if not allow_extensions and os.path.splitext(executable)[1]:
        raise ValueError(
            "find_executable_on_path({},...) failed because first "
            "argument must not have an extension.".format(executable)
        )

    if os.path.dirname(executable):
        raise ValueError(
            "find_executable_on_path({},...) failed because first " "argument must not have a path.".format(executable)
        )

    if path is None:
        effective_path = get_system_path()
    else:
        effective_path = path
    effective_pathext = (
        pathext if pathext is not None else _platform_executable_extensions(platforms.OperatingSystem.current())
    )

    return _find_executable_on_path(executable, effective_path, effective_pathext)
