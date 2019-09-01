#!/usr/bin/env python3
"""
Change type detectors.

Parses a configuration with what type of change do you want to produce.
"""
import abc
import logging
import six

from auto_tag import constants
from auto_tag import exception


@six.add_metaclass(abc.ABCMeta)
class BaseDetector():
    """Base detector class."""

    def __init__(self, name, change_type, case_sensitive=True,
                 strip=True, **kwargs):
        """Initialize the detector."

        :param name: Name of the detector
        :param change_type: If this detector fires what type of change it will
                            create
        :param case_sensitive: If the detector is case sensitive
        :param strip: Strip the evaluated value before processing
        :param logger: If specified what logger to use
        """
        self._name = name
        self._change_type = change_type
        self._case_sensitive = case_sensitive
        self._strip = strip
        self._logger = (
            kwargs.get('logger', None) or logging.getLogger(__name__))

    @property
    def name(self):
        """Return name of the detector."""
        return self._name

    @property
    def strip(self):
        """Return strip value of the detector."""
        return self._strip

    @property
    def case_sensitive(self):
        """Return case_sensitive value of the detector."""
        return self._case_sensitive

    @property
    def change_type(self):
        """Return the type of change this detector imposes."""
        return self._change_type

    def validate_detector_params(self):
        """Check if all the parameters given to the detector make sens."""
        if self._change_type not in constants.CHANGE_TYPES.values():
            raise exception.DetectorValidationException(
                ('Change type {} is not in not valid. Accepted'
                 ' change types are {}').format(
                     self._change_type, constants.CHANGE_TYPES.keys()))

    @abc.abstractmethod
    def evaluate(self, commit):
        """Evaluate the commit and see if this detector is triggered.

        :param commit: The commit to evaluate

        :returns: True if this detector got triggered
        :rtype: book
        """


class BasePatternBaseDetector(BaseDetector):
    """Check if the commit message respects a pattern"""

    def __init__(self, *args, **kwargs):
        """Initialize the detector.

        :param pattern: The pattern to match if it starts with

        :param *args: Check with the base class
        :param **kwargs: Check with the base class
        """
        super(BasePatternBaseDetector, self).__init__(
            *args, **kwargs)

        self._pattern = kwargs.get('pattern', None)
        if isinstance(self._pattern, str) and not self._case_sensitive:
            self._pattern = self._pattern.lower()

    @property
    def pattern(self):
        """Return pattern value of the detector."""
        return self._pattern

    def validate_detector_params(self):
        """Check if all the parameters given to the detector make sens."""
        super(BasePatternBaseDetector, self).validate_detector_params()
        if not isinstance(self._pattern, str):
            raise exception.DetectorValidationException(
                ('Patter: {} is not valid.'
                 'it must be specified and of type string').format(
                     self._pattern))

    def _prepare_commit_message(self, commit):
        """Get the prepared commit message according to the config."""
        message = commit.message
        if not self._case_sensitive:
            message = message.lower()
        if self._strip:
            message = message.strip()
        return message


class CommitMessageHeadStartsWithDetector(BasePatternBaseDetector):
    """Check if the head of the commit message has a particular pattern."""

    def evaluate(self, commit):
        """Check if the commit message head starts with a given string

        :param commit: The commit to evaluate

        :returns: True if this detector got triggered
        :rtype: book
        """
        message = self._prepare_commit_message(commit)

        if self._case_sensitive:
            return message.startswith(self._pattern)
        return message.startswith(self._pattern.lower())


class CommitMessageContainsDetector(BasePatternBaseDetector):
    """Check if the message of the commit contains a particular pattern."""

    def evaluate(self, commit):
        """Check if the commit message contains a given string

        :param commit: The commit to evaluate

        :returns: True if this detector got triggered
        :rtype: book
        """
        message = self._prepare_commit_message(commit)

        if self._case_sensitive:
            return self._pattern in message
        return self._pattern.lower() in message


DETECTORS = [
    CommitMessageHeadStartsWithDetector,
    CommitMessageContainsDetector
]


def detector_factory(detector_name):
    """Return the appropriate detector class based on the name.

    :param detector_name: Name of the detector
    :return: Detector class
    :rtype: auto_tag.detectors.BaseDetector
    """
    detector_map = {detector.__name__: detector for detector in DETECTORS}

    if detector_name not in detector_map:
        raise exception.DetectorNotFound(
            'Detector {} not found. Available detectors: {}'.format(
                detector_name, detector_map.keys()))
    return detector_map[detector_name]
