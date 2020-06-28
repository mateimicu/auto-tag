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
    version='0.8.2',
    description='Automatically tag a branch based on commit message',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Matei-Marius Micu',
    author_email='contact@mateimicu.com	',
    license='MIT',
    url='https://github.com/mateimicu/auto-tag',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: System :: Software Distribution',
    ],
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'auto-tag=auto_tag.__main__:main',
        ]
    },
    install_requires=[
        'gitpython>=3.1.1',
        'semantic_version>=2.8.5',
        'confuse>=1.0.0',
        'six>=1.13.0',
    ]
)
