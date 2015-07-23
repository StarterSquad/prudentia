# !/usr/bin/env python

import sys

from prudentia import __version__, __author__

from codecs import open

try:
    from setuptools import setup
except ImportError:
    print "Prudentia needs setuptools in order to build. " \
          "Install it using your package manager (usually python-setuptools) or via pip (pip install setuptools)."
    sys.exit(1)

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()
with open('HISTORY.rst', 'r', 'utf-8') as f:
    history = f.read()

setup(
    name='prudentia',
    version=__version__,
    description='Continuous Deployment toolkit.',
    author=__author__,
    author_email='tiziano@startersquad.com',
    long_description=readme + '\n\n' + history,
    url='https://github.com/StarterSquad/prudentia',
    license='MIT',
    install_requires=['ansible', 'requests[security]', 'dopy', 'boto'],
    packages=['prudentia', 'prudentia.utils'],
    include_package_data=True,
    scripts=['bin/prudentia'],
    platforms='Posix; MacOS X;'
)
