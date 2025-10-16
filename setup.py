import codecs
import logging
import os
import sys

from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from importlib import import_module

from setuptools import Command, Extension
from setuptools.command.test import test as TestCommand

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

logger = logging.getLogger(__name__)

version = import_module("xTool.version").version

PY3 = sys.version_info[0] == 3


class Tox(TestCommand):
    user_options = [("tox-args=", None, "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = ""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox

        errno = tox.cmdline(args=self.tox_args.split())
        sys.exit(errno)


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info")


def git_version(version):
    """
    Return a version to identify the state of the underlying git repo. The version will
    indicate whether the head of the current git-backed working directory is tied to a
    release tag or not : it will indicate the former with a 'release:{version}' prefix
    and the latter with a 'dev0' prefix. Following the prefix will be a sha of the current
    branch head. Finally, a "dirty" suffix is appended to indicate that uncommitted changes
    are present.
    """
    try:
        import git

        repo = git.Repo(".git")
    except ImportError:
        logger.warning("gitpython not found: Cannot compute the git version.")
        return ""
    except Exception as e:
        logger.warning("Cannot compute the git version. {}".format(e))
        return ""
    if repo:
        sha = repo.head.commit.hexsha
        if repo.is_dirty():
            return ".dev0+{sha}.dirty".format(sha=sha)
        # commit is clean
        return ".release:{version}+{sha}".format(version=version, sha=sha)
    else:
        return "no_git_version"


def read(filename):
    """Read and return `filename` in root dir of project and return string ."""
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, filename), "r").read()


test_requirements = [
    "pytest",
    "pytest-asyncio",
]


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        """初始化可选项 ."""
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        """执行测试 ."""
        import shlex

        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


# Make Twisted regenerate the dropin.cache, if possible.  This is necessary
# because in a site-wide install, dropin.cache cannot be rewritten by
# normal users.
def refresh_plugin_cache():
    """刷新缓冲 ."""
    try:
        from twisted.plugin import IPlugin  # noqa
        from twisted.plugin import getPlugins  # noqa

        list(getPlugins(IPlugin))
    except Exception as e:
        print(e)  # noqa
        # log.warn("*** Failed to update Twisted plugin cache. ***")
        # log.warn(str(e))


README = os.path.join(os.path.dirname(__file__), "README.md")
long_description = open(README, encoding="utf-8").read() + "\n\n"

install_requires = []
if os.path.exists("requirements.txt"):
    install_requires = read("requirements.txt").split()
    if "win" in sys.platform:
        for item in ["pexpect"]:
            try:
                install_requires.remove(item)
            except ValueError:
                pass

install_requires.extend([])


if PY3:
    ext_modules = [
        Extension("xTool/decorators._helpers", ["xTool/decorators/_helpers.c"]),
        Extension(
            "xTool.cython.example",
            ["xTool/cython/example.pyx"],
            extra_compile_args=["-std=c++11", "-O3"],
            include_dirs=["."],
            language="c++",
            extra_link_args=["-std=c++11"],
        ),
        Extension(
            "xTool.crypto.codec.pickle_codec_c",
            ["xTool/crypto/codec/pickle_codec_c.pyx"],
            extra_compile_args=["-O3"],
            include_dirs=["."],
        ),
        Extension(
            "xTool.cython.bytes_order",
            ["xTool/cython/bytes_order.pyx"],
            extra_compile_args=["-O3"],
            include_dirs=["."],
        ),
    ]
else:
    ext_modules = []


def do_setup():
    setup(
        name="xTool",
        version=version,
        description="A python script tools",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="jinyinqiao",
        author_email="jinyinqiao@gmail.com",
        license="Apache License 2.0",
        packages=find_packages(exclude=["tests*"]),
        include_package_data=True,
        install_requires=install_requires,
        zip_safe=False,
        scripts=None,
        keywords="xTool",
        classifiers=[
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Environment :: Console",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
        ],
        setup_requires=[
            "gitpython",
            "flake8",
            "docutils>=0.14",
        ],
        extras_require={
            "dev": ["pytest", "pyyaml", "pytest-sanic"],
            "fast": ["uvloop"],
        },
        # ext_modules=cythonize(ext_modules),
        test_suite="tests",
        tests_require=test_requirements,
        cmdclass={"test": PyTest},
        # cmdclass={
        #    'test': Tox,
        #    'extra_clean': CleanCommand,
        # },
    )


if __name__ == "__main__":
    do_setup()
