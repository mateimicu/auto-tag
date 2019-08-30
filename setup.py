#!/usr/bin/env python3
"""
Setup file for the package.
"""

import os
import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = os.path.abspath(pathlib.Path(__file__).parent)

# The text of the README file
README = open(
    os.path.join(HERE, 'README.md'),
    'r').read()

# This call to setup() does all the work
setup(
    name='auto-tag',
    version='0.1.0',
    description='Automatically tag a branch based on commit message',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Matei-Marius Micu',
    author_email='contact@mateimicu.com	',
    license='MIT',
    url="https://github.com/mateimicu/auto-tag",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'auto-tag=auto_tag.__main__:main',
        ]
    },
    install_reqs=[
        'gitpython',
        'semantic_version',
    ]
)
