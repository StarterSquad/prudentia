# !/usr/bin/env python

from codecs import open

from setuptools import setup

from prudentia import __version__, __author__

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()
with open('HISTORY.rst', 'r', 'utf-8') as f:
    history = f.read()
with open('requirements.txt', 'r', 'utf-8') as f:
    requires = f.readlines()

setup(
    name='prudentia',
    version=__version__,
    description='Continuous Deployment toolkit.',
    author=__author__,
    author_email='tiziano@startersquad.com',
    long_description=readme + '\n\n' + history,
    url='https://github.com/StarterSquad/prudentia',
    license='MIT',
    install_requires=requires,
    packages=['prudentia', 'prudentia.utils'],
    include_package_data=True,
    scripts=['bin/prudentia'],
    platforms='Posix; MacOS X;'
)
