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
