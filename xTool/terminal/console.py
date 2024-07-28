import os
import sys


def is_interactive(output=False, error=False, heuristic=False):
    """Determines if the current terminal session is interactive.

    sys.stdin must be a terminal input stream.

    Args:
      output: If True then sys.stdout must also be a terminal output stream.
      error: If True then sys.stderr must also be a terminal output stream.
      heuristic: If True then we also do some additional heuristics to check if
                 we are in an interactive context. Checking home path for example.

    Returns:
      True if the current terminal session is interactive.
    """
    if not sys.stdin.isatty():
        return False
    if output and not sys.stdout.isatty():
        return False
    if error and not sys.stderr.isatty():
        return False

    if heuristic:
        # Check the home path. Most startup scripts for example are executed by
        # users that don't have a home path set. Home is OS dependent though, so
        # check everything.
        # *NIX OS usually sets the HOME env variable. It is usually '/home/user',
        # but can also be '/root'. If it's just '/' we are most likely in an init
        # script.
        # Windows usually sets HOMEDRIVE and HOMEPATH. If they don't exist we are
        # probably being run from a task scheduler context. HOMEPATH can be '\'
        # when a user has a network mapped home directory.
        # Cygwin has it all! Both Windows and Linux. Checking both is perfect.
        home = os.getenv('HOME')
        homepath = os.getenv('HOMEPATH')
        if not homepath and (not home or home == '/'):
            return False
    return True
