#!/usr/bin/env python3
"""
CLI parser for auto-tag.
"""
import logging
import argparse

from auto_tag import constants
from auto_tag import tag_search_strategy


def get_parser():
    """Return the argument parser setup."""
    parser = argparse.ArgumentParser(
        description='Tag branch based on commit messages')
    parser.add_argument('-b', '--branch', type=str, default='master',
                        help='On what branch to work on. Default `master`')
    parser.add_argument('-r', '--repo', type=str, default='.',
                        help='Path to repository. Default `.`')
    parser.add_argument('-u', '--upstream_remote', type=str, nargs='*',
                        help=('To what remote to push to.'
                              'Can be specified multiple time.'))
    #  pylint:disable=no-member, protected-access
    parser.add_argument('-l', '--logging', type=str, default='INFO',
                        help='Logging level.',
                        choices=list(logging._nameToLevel.keys()))

    parser.add_argument('--name', type=str, default=None,
                        help=('User name used for creating git objects.'
                              'If not specified the system one will be used.'))
    parser.add_argument('--email', type=str, default=None,
                        help=('Email name used for creating git objects.'
                              'If not specified the system one will be used.'))

    parser.add_argument('-c', '--config', type=str, default=None,
                        help='Path to detectors configuration.')

    parser.add_argument('--skip-tag-if-one-already-present',
                        action='store_true',
                        help=('If a tag is already present on the latest '
                              'commit don\'t apply a new tag'))

    parser.add_argument('--append-v-to-tag', action='store_true',
                        help='Append a v to the tag (ex v1.0.5)')

    parser.add_argument('--tag-search-strategy',
                        choices=constants.SEARCH_STRATEGYS,
                        default=tag_search_strategy.DEFAULT_STRAGETY_NAME,
                        help='Strategy for searching the tag.')

    return parser
