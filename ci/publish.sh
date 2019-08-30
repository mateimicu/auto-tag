#!/usr/bin/env bash
# install dependency's 
pip3 install --user twine 

# bumpversion
# package the project 
./setup.py sdist bdist_wheel

# check the package 
twine check dist/*
# check the publishing 
twine upload --repository testpypi dist/*

# publish the package
twine upload --repository pypi dist/*
