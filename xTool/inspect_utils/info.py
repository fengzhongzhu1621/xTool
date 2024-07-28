import inspect

from . import docstrings
from .lineno import get_file_and_line


def Info(component):
    """Returns a dict with information about the given component.

    The dict will have at least some of the following fields.
      type_name: The type of `component`.
      string_form: A string representation of `component`.
      file: The file in which `component` is defined.
      line: The line number at which `component` is defined.
      docstring: The docstring of `component`.
      init_docstring: The init docstring of `component`.
      class_docstring: The class docstring of `component`.
      call_docstring: The call docstring of `component`.
      length: The length of `component`.

    Args:
      component: The component to analyze.
    Returns:
      A dict with information about the component.
    """
    try:
        from IPython.core import oinspect  # pylint: disable=import-outside-toplevel,g-import-not-at-top

        inspector = oinspect.Inspector()
        info = inspector.info(component)

        if info["docstring"] == "<no docstring>":
            info["docstring"] = None
    except ImportError:
        info = _info_backup(component)

    try:
        unused_code, lineindex = inspect.findsource(component)
        info["line"] = lineindex + 1
    except (TypeError, OSError):
        info["line"] = None

    if "docstring" in info:
        info["docstring_info"] = docstrings.parse(info["docstring"])

    return info


def _info_backup(component):
    """Returns a dict with information about the given component.

    This function is to be called only in the case that IPython's
    oinspect module is not available. The info dict it produces may
    contain less information that contained in the info dict produced
    by oinspect.

    Args:
      component: The component to analyze.
    Returns:
      A dict with information about the component.
    """
    info = {}

    info["type_name"] = type(component).__name__
    info["string_form"] = str(component)

    filename, lineno = get_file_and_line(component)
    info["file"] = filename
    info["line"] = lineno
    info["docstring"] = inspect.getdoc(component)

    try:
        info["length"] = str(len(component))
    except (TypeError, AttributeError):
        pass

    return info
