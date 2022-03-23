#!/usr/bin/env python

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='qpycmd',
    version="v2.2",
    description='terminal brigade between python mobile.',
    long_description="",
    author="guangrei",    author_email='myawn{[AT]}pm.me',
    packages=['qpycmd'],
    scripts=['qcmd'],
    license='MIT',
    platforms='any',
)
