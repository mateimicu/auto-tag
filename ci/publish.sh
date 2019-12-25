#!/usr/bin/env bash
# install dependency's 
pipenv install --dev

# bumpversion
# package the project 
pipenv run ./setup.py sdist bdist_wheel

# check the package 
pipenv run twine check dist/*
# check the publishing 
pipenv run twine upload --repository testpypi dist/*

# publish the package
pipenv run twine upload --repository pypi dist/*
