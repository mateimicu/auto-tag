#!/usr/bin/env python3
"""
Test simple flows of the AutoTag application
"""
import os

from auto_tag import detectors_config
from auto_tag import detectors
# pylint:disable=invalid-name


def test_detector_config():
    """Test to see if the factory returns what we expect."""
    path_to_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'data', 'detectors_example.yaml')

    config = detectors_config.DetectorsConfig(path_to_file)
    assert config.detectors
    assert len(config.detectors) == 6

    for detector in config.detectors:
        if detector.name == 'detector_1':
            assert isinstance(
                detector, detectors.CommitMessageHeadStartsWithDetector)
            assert detector.pattern == 'pattern-1'
            assert detector.case_sensitive
            assert detector.strip

        if detector.name == 'detector_2':
            assert isinstance(
                detector, detectors.CommitMessageHeadStartsWithDetector)
            assert detector.pattern == 'pattern-2'
            assert detector.case_sensitive
            assert detector.strip

        if detector.name == 'detector_3':
            assert isinstance(
                detector, detectors.CommitMessageHeadStartsWithDetector)
            assert detector.pattern == 'pattern-3'
            assert detector.case_sensitive
            assert not detector.strip

        if detector.name == 'detector_4':
            assert isinstance(
                detector, detectors.CommitMessageContainsDetector)
            assert detector.pattern == 'pattern-4'
            assert detector.case_sensitive
            assert detector.strip

        if detector.name == 'detector_5':
            assert isinstance(
                detector, detectors.CommitMessageContainsDetector)
            assert detector.pattern == 'pattern-5'
            assert detector.case_sensitive
            assert detector.strip

        if detector.name == 'detector_6':
            assert isinstance(
                detector, detectors.CommitMessageContainsDetector)
            assert detector.pattern == 'pattern-6'
            assert not detector.case_sensitive
            assert not detector.strip
