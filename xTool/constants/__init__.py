import os
import platform
import sys

from xTool.collections import ConstantDict

from .field import *  # noqa
from .number import *  # noqa
from .queue import *  # noqa
from .regex import *  # noqa
from .time import *  # noqa

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3

# Determine platform being used.
system = platform.system()
USE_MAC = USE_WINDOWS = USE_LINUX = USE_CYGWIN = USE_X11 = False
if system == "Darwin":
    USE_MAC = True
elif system == "Windows" or system == "Microsoft":
    USE_WINDOWS = True
elif system == "Linux":
    USE_LINUX = True
elif system.startswith("CYGWIN"):
    USE_CYGWIN = True
else:  # Default to X11
    USE_X11 = True
OS_IS_WINDOWS = os.name == "nt"

HTTP_METHODS = ("GET", "POST", "PUT", "HEAD", "OPTIONS", "PATCH", "DELETE")

NO_VALUE = object()  # type: Any

sentinel = object()  # type: Any

CHAR = {chr(i) for i in range(0, 128)}
CTL = {chr(i) for i in range(0, 32)} | {
    chr(127),
}
SEPARATORS = {
    "(",
    ")",
    "<",
    ">",
    "@",
    ",",
    ";",
    ":",
    "\\",
    '"',
    "/",
    "[",
    "]",
    "?",
    "=",
    "{",
    "}",
    " ",
    chr(9),
}
# 按位异或
TOKEN = CHAR ^ CTL ^ SEPARATORS

EMPTY_INT = 0
EMPTY_STRING = ""
EMPTY_LIST = []
EMPTY_DICT = ConstantDict({})
EMPTY_VARIABLE = {"inputs": [], "outputs": []}
DEFAULT_BK_BIZ_ID = -1
EMPTY = "EMPTY"

TABLE = "TABLE"
BASE_MODEL = "BASE-MODEL"
