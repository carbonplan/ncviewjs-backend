#!/usr/bin/env python

"""The setup script"""
import pathlib

from setuptools import find_packages, setup

LONG_DESCRIPTION = pathlib.Path('README.md').read_text()

setup(
    url='https://github.com/carbonplan/ncviewjs-backend',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    keywords='carbon, data, climate',
)
