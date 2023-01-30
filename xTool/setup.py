# -*- coding: utf-8 -*-

import codecs
import os
import platform
import re
import sys
import warnings
from distutils.errors import CCompilerError
from distutils.errors import DistutilsExecError
from distutils.errors import DistutilsPlatformError

from setuptools.command.test import test as TestCommand

extension_support = True  # Assume we are building C extensions.

# Check if Cython is available and use it to generate extension modules. If
# Cython is not installed, we will fall back to using the pre-generated C files
# (so long as we're running on CPython).
try:
    from Cython.Build import cythonize
    from Cython.Distutils import build_ext
    from Cython.Distutils.extension import Extension
except ImportError:
    cython_installed = False
else:
    if platform.python_implementation() != 'CPython':
        cython_installed = extension_support = False
        warnings.warn('C extensions disabled as you are not using CPython.')
    else:
        cython_installed = True

if 'sdist' in sys.argv and not cython_installed:
    raise Exception('Building sdist requires that Cython be installed.')

if sys.version_info[0] < 3:
    FileNotFoundError = EnvironmentError

if cython_installed:
    src_ext = '.pyx'
else:
    src_ext = '.c'


    def cythonize(obj):
        return obj


def add_pywin32_to_install_requires():
    if "windows" in sys.platform.lower():
        install_requires = []
        try:
            import win32file
        except ImportError:
            # Only require pywin32 if not already installed
            # version 223 introduced ability to install from pip
            install_requires.append("pywin32>=223")
        return install_requires


def _have_sqlite_extension_support():
    import shutil
    import tempfile
    from distutils.ccompiler import new_compiler
    from distutils.sysconfig import customize_compiler

    libraries = ['sqlite3']
    c_code = ('#include <sqlite3.h>\n\n'
              'int main(int argc, char **argv) { return 0; }')
    tmp_dir = tempfile.mkdtemp(prefix='tmp_pw_sqlite3_')
    bin_file = os.path.join(tmp_dir, 'test_pw_sqlite3')
    src_file = bin_file + '.c'
    with open(src_file, 'w') as fh:
        fh.write(c_code)

    compiler = new_compiler()
    customize_compiler(compiler)
    success = False
    try:
        compiler.link_executable(
            compiler.compile([src_file], output_dir=tmp_dir),
            bin_file,
            libraries=['sqlite3'])
    except CCompilerError:
        print('unable to compile sqlite3 C extensions - missing headers?')
    except DistutilsExecError:
        print('unable to compile sqlite3 C extensions - no c compiler?')
    except DistutilsPlatformError:
        print('unable to compile sqlite3 C extensions - platform error')
    except FileNotFoundError:
        print('unable to compile sqlite3 C extensions - no compiler!')
    else:
        success = True
    shutil.rmtree(tmp_dir)
    return success


# This is set to True if there is extension support and libsqlite3 is found.
sqlite_extension_support = False

if extension_support:
    if os.environ.get('NO_SQLITE'):
        warnings.warn('SQLite extensions will not be built at users request.')
    elif not _have_sqlite_extension_support():
        warnings.warn('Could not find libsqlite3, SQLite extensions will not '
                      'be built.')
    else:
        sqlite_extension_support = True


# Exception we will raise to indicate a failure to build C extensions.
class BuildFailure(Exception):
    pass


class _PeeweeBuildExt(build_ext):
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            raise BuildFailure()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError, DistutilsPlatformError):
            raise BuildFailure()


class PyTest(TestCommand):
    """python setup.py test support pytest"""

    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def open_local(paths, mode="r", encoding="utf8"):
    """打开本地文件 ."""
    path = os.path.join(*paths)

    return codecs.open(path, mode, encoding)


def get_version(module_name):
    with open(f'{module_name}/__version__.py') as f:
        empty, version = f.read().split('__version__ = ')
    assert empty == ''
    version = version.strip().strip("'")
    assert version.startswith('0.')
    return version


def read_version_file(package):
    with open_local([package, "__version__.py"], encoding="latin1") as fp:
        try:
            version = re.findall(
                r"^__version__ = \"([^']+)\"\r?$", fp.read(), re.M
            )[0]
        except IndexError:
            raise RuntimeError("Unable to determine version.")
    return version


def read_version_file2(package):
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = os.path.join(os.path.dirname(__file__), package, "__init__.py")
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        raise RuntimeError("Cannot find version in {}".format(init_py))


def read_readme_rst():
    with open_local(["README.rst"]) as rm:
        long_description = rm.read()
    return long_description


def get_readme():
    try:
        with open('README.rst') as f:
            return f.read().strip()
    except IOError:
        return ''
    

def load_requirements(fname):
    """ load requirements from a pip requirements file

    examples:
        extras_require={
            'develop': load_requirements('requirements.dev.txt'),
        },
    """
    with open(fname) as f:
        line_iter = (line.strip() for line in f.readlines())
        return [line for line in line_iter if line and line[0] != '#']
