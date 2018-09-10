# -*- coding: utf-8 -*-

import imp
import logging
import os
import pip
import sys
import codecs
import sys
from io import open

try:
    from setuptools import setup  # noqa
except ImportError:
    from distutils.core import setup  # noqa
from setuptools.command.test import test as TestCommand  # noqa
from setuptools import find_packages, Command

# try:
#     import twisted  # noqa
# except ImportError:
#     # raise SystemExit("twisted not found.  Make sure you "
#     #                 "have installed the Twisted core package.")
#     pass

logger = logging.getLogger(__name__)

# Kept manually in sync with airflow.__version__
version = imp.load_source(
    'xTool.version', os.path.join('xTool', 'version.py')).version

PY3 = sys.version_info[0] == 3


class Tox(TestCommand):
    user_options = [('tox-args=', None, "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = ''

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
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


def git_version(version):
    """
    Return a version to identify the state of the underlying git repo. The version will
    indicate whether the head of the current git-backed working directory is tied to a
    release tag or not : it will indicate the former with a 'release:{version}' prefix
    and the latter with a 'dev0' prefix. Following the prefix will be a sha of the current
    branch head. Finally, a "dirty" suffix is appended to indicate that uncommitted changes
    are present.
    """
    repo = None
    try:
        import git
        repo = git.Repo('.git')
    except ImportError:
        logger.warning('gitpython not found: Cannot compute the git version.')
        return ''
    except Exception as e:
        logger.warning('Cannot compute the git version. {}'.format(e))
        return ''
    if repo:
        sha = repo.head.commit.hexsha
        if repo.is_dirty():
            return '.dev0+{sha}.dirty'.format(sha=sha)
        # commit is clean
        return '.release:{version}+{sha}'.format(version=version, sha=sha)
    else:
        return 'no_git_version'


def write_version(filename=os.path.join(*['xTool',
                                          'git_version'])):
    text = "{}".format(git_version(version))
    with open(filename, 'w') as a:
        a.write(text)


def read(filename):
    """Read and return `filename` in root dir of project and return string ."""
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, filename), 'r').read()


with open('README.rst', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', encoding='utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

test_requirements = [
    'pytest',
]


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


# Make Twisted regenerate the dropin.cache, if possible.  This is necessary
# because in a site-wide install, dropin.cache cannot be rewritten by
# normal users.
def refresh_plugin_cache():
    try:
        from twisted.plugin import getPlugins  # noqa
        from twisted.plugin import IPlugin  # noqa
        list(getPlugins(IPlugin))
    except Exception as e:
        print(e)  # noqa
        # log.warn("*** Failed to update Twisted plugin cache. ***")
        # log.warn(str(e))


from setuptools import setup, find_packages
# from distutils.core import setup

README = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(README, encoding='utf-8').read() + '\n\n'

install_requires = []
if os.path.exists("requirements.txt"):
    install_requires = read("requirements.txt").split()
    if "win" in sys.platform:
        for item in ['pexpect']:
            try:
                install_requires.remove(item)
            except ValueError as e:
                pass

install_requires.extend([
    # 'python-daemon>=2.1.1, <2.2',  # 用于构建守护进程
    'pendulum==1.4.2',  # 日期库
    'tabulate>=0.7.5, <0.8.0',
    'python-dateutil>=2.3, <3',
    'croniter>=0.3.17, <0.4'
])

doc = [
    'sphinx>=1.2.3',
    'sphinx-argparse>=0.1.13',
    'sphinx-rtd-theme>=0.1.6',
    'Sphinx-PyPI-upload>=0.2.1'
]


def do_setup():
    write_version()

    setup(
        name='xTool',
        version=version,
        description='A python script tools',
        long_description=long_description,
        author='jinyinqiao',
        author_email='jinyinqiao@gmail.com',
        license='Apache License 2.0',
        packages=find_packages(exclude=['tests*']),
        # packages = ['xTool',
        #            #"twisted.plugins",
        # ],
        include_package_data=True,
        install_requires=install_requires,
        zip_safe=False,
        scripts=None,
        keywords='xTool',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: English',
            'Environment :: Console',
            "Programming Language :: Python :: 2",
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
        setup_requires=[
            "flake8",
            'docutils>=0.14, <1.0',
        ],
        extras_require={
            'doc': doc,
        },
        test_suite='tests',
        tests_require=test_requirements,
        cmdclass={'test': PyTest},
        #cmdclass={
        #    'test': Tox,
        #    'extra_clean': CleanCommand,
        #},
    )


# refresh_plugin_cache()

if __name__ == "__main__":
    do_setup()
