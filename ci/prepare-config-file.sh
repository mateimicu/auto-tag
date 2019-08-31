#!/usr/bin/env bash
# Prepare config file for twine
echo > ~/.pypirc << EOF
[distutils]
index-servers=
    pypi
    testpypi

[pypi]
username: $PYPI_USERNAME
password: $PYPI_PASSWORD

[testpypi]
repository: https://test.pypi.org/legacy/
username:  $TEST_PYPI_USERNAME
password: $TEST_PYPI_PASSWORD
EOF
