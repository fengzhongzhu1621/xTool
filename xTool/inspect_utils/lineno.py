import inspect


def get_file_and_line(component):
    """Returns the filename and line number of component.

    Args:
      component: A component to find the source information for, usually a class
          or routine.
    Returns:
      filename: The name of the file where component is defined.
      lineno: The line number where component is defined.
    """
    if inspect.isbuiltin(component):
        return None, None

    try:
        filename = inspect.getsourcefile(component)
    except TypeError:
        return None, None

    try:
        unused_code, lineindex = inspect.findsource(component)
        lineno = lineindex + 1
    except (OSError, IndexError):
        lineno = None

    return filename, lineno
