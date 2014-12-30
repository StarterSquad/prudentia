# !/usr/bin/env python

import os
import sys

from prudentia import __version__, __author__


try:
    from setuptools import setup
except ImportError:
    print "Prudentia needs setuptools in order to build. " \
          "Install it using your package manager (usually python-setuptools) or via pip (pip install setuptools)."
    sys.exit(1)

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel upload')
    sys.exit()

setup(
    name='prudentia',
    version=__version__,
    description='Continuous Deployment toolkit.',
    author=__author__,
    author_email='tiziano@startersquad.com',
    url='https://github.com/StarterSquad/prudentia',
    license='MIT',
    install_requires=['ansible', 'dopy', 'boto'],
    packages=['prudentia', 'prudentia.utils'],
    include_package_data=True,
    scripts=[
        'bin/prudentia'
    ],
    platforms='Posix; MacOS X;'
)
