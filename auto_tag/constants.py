#!/usr/bin/env python3
"""
Constants used in the AutoTag project
"""
MAJOR = 100
MINOR = 10
PATCH = 1

CHANGE_TYPE_PAIRS = (
    (MAJOR, 'MAJOR'),
    (MINOR, 'MINOR'),
    (PATCH, 'PATCH'),
)

SEARCH_STRATEGY_BIGGEST_TAG_IN_REPO = 'biggest-tag-in-repo'
SEARCH_STRATEGY_BIGGEST_TAG_IN_BRANCH = 'biggest-tag-in-branch'
SEARCH_STRATEGY_LATEST_TAG_IN_REPO = 'latest-tag-in-repo'
SEARCH_STRATEGY_LATEST_TAG_IN_BRANCH = 'latest-tag-in-branch'

SEARCH_STRATEGYS = [
    SEARCH_STRATEGY_BIGGEST_TAG_IN_REPO,
    SEARCH_STRATEGY_BIGGEST_TAG_IN_BRANCH,
    SEARCH_STRATEGY_LATEST_TAG_IN_REPO,
    SEARCH_STRATEGY_LATEST_TAG_IN_BRANCH,
]

# pylint: disable=unnecessary-comprehension
CHANGE_TYPES = {value: name for value, name in CHANGE_TYPE_PAIRS}
CHANGE_TYPES_REVERSE = {name: value for value, name in CHANGE_TYPE_PAIRS}

PREFIX_TO_ELIMINATE = ['v']

DEFAULT_CONFIG_DETECTORS = """
detectors:

  check_for_feature_heading:
    type: CommitMessageHeadStartsWithDetector
    produce_type_change: MINOR
    params:
      pattern: 'feature'


  check_for_breaking_change:
    type: CommitMessageContainsDetector
    produce_type_change: MAJOR
    params:
      pattern: 'BREAKING_CHANGE'
      case_sensitive: false
"""
