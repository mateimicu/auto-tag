#!/usr/bin/env python3
"""
CLI parser for auto-tag.
"""
import logging
import argparse


def get_parser():
    """Return the argument parser setup."""
    parser = argparse.ArgumentParser(
        description='Tag branch based on commit messages')
    parser.add_argument('-b', '--branch', type=str, default='master',
                        help='On what branch to work on. Default `master`')
    parser.add_argument('-r', '--repo', type=str, default='.',
                        help='Path to repository. Default `.`')
    parser.add_argument('-u', '--upstream_remote', type=str, nargs='+',
                        help=('To what remote to push to.'
                              'Can be specified multiple time.'))
    parser.add_argument('-l', '--logging', type=str, default='INFO',
                        help='Logging level.',
                        choices=list(logging._nameToLevel.keys()))

    return parser
