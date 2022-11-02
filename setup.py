#!/usr/bin/env python

import sys
from qpycmd.climate import Qpyutil
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='qpycmd',
    version="v4.1.6",
    description='terminal for python mobile.',
    long_description="",
    author="guangrei",    author_email='myawn@pm.me',
    packages=['qpycmd'],
    scripts=['qcmd'],
    license='MIT',
    platforms='any',
)

if Qpyutil.is_qpy():
    Qpyutil.update_terminal()
