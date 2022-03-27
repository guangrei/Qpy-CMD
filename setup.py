#!/usr/bin/env python

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='qpycmd',
    version="v3.0",
    description='terminal for python mobile.',
    long_description="",
    author="guangrei",    author_email='myawn@pm.me',
    packages=['qpycmd'],
    scripts=['qcmd'],
    license='MIT',
    platforms='any',
)
