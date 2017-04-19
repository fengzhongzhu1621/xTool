#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Command: py.test tests/test_example.py -v

"""

import codecs
import os
import sys
from io import open

try:
    from setuptools import setup  # noqa
except ImportError:
    from distutils.core import setup  # noqa
from setuptools.command.test import test as TestCommand  # noqa

try:
    import twisted  # noqa
except ImportError:
    #raise SystemExit("twisted not found.  Make sure you "
    #                 "have installed the Twisted core package.")
    pass


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
#from distutils.core import setup
version = '0.1.0'

README = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(README, encoding='utf-8').read() + '\n\n'

install_requires = None
if os.path.exists("requirements.txt"):
    install_requires = read("requirements.txt").split()
    if "win" in sys.platform:
        for item in ['pexpect']:
            try:
                install_requires.remove(item)
            except ValueError as e:
                pass

setup(
    name = 'xTools',
    version = version,
    description = 'A python script tools',
    long_description=long_description,
    author = 'jinyinqiao',
    author_email = 'jinyinqiao@gmail.com',
    license = 'MIT',
    packages = find_packages(),
    #packages = ['xTools',
    #            #"twisted.plugins",
    #],
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    keywords='xTools',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    setup_requires=[
        "flake8"
    ],
    extras_require={
        'docs': ['Sphinx', ],
    },
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={'test': PyTest},
)

refresh_plugin_cache()
