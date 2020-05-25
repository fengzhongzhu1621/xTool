# -*- coding: utf-8 -*-
import os
import platform
import sys
import warnings
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError
from distutils.errors import DistutilsExecError
from distutils.errors import DistutilsPlatformError

from setuptools import setup
from setuptools.extension import Extension

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
    def cythonize(obj): return obj


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
