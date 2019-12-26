#!/usr/bin/env python3
"""
Change type detectors.

Parses a configuration with what type of change do you want to produce.
"""
from typing import Any, NoReturn
import abc
import logging
import re
import six

import git

from auto_tag import constants
from auto_tag import exception


@six.add_metaclass(abc.ABCMeta)
class BaseDetector():
    """Base detector class."""

    def __init__(self, name: str, change_type: str,
                 strip: bool = True, **kwargs: Any) -> None:
        """Initialize the detector."

        :param name: Name of the detector
        :param change_type: If this detector fires what type of change it will
                            create
        :param strip: Strip the evaluated value before processing
        :param logger: If specified what logger to use
        """
        self._name = name
        self._change_type_name = change_type
        self._strip = strip
        self._logger = (
            kwargs.get('logger', None) or logging.getLogger(__name__))

    @property
    def name(self) -> str:
        """Return name of the detector."""
        return self._name

    @property
    def strip(self) -> bool:
        """Return strip value of the detector."""
        return self._strip

    @property
    def change_type_name(self) -> str:
        """Return the type of change this detector imposes."""
        return self._change_type_name

    @property
    def change_type(self) -> int:
        """Return the type of change this detector imposes."""
        return constants.CHANGE_TYPES_REVERSE[self._change_type_name]

    def validate_detector_params(self) -> NoReturn: # type: ignore
        """Check if all the parameters given to the detector make sens."""
        if self._change_type_name not in constants.CHANGE_TYPES.values():
            raise exception.DetectorValidationException(
                ('Change type {} is not in not valid. Accepted'
                 ' change types are {}').format(
                     self._change_type_name, constants.CHANGE_TYPES.keys()))

    @abc.abstractmethod
    def evaluate(self, commit: git.objects.commit.Commit) -> bool:
        """Evaluate the commit and see if this detector is triggered.

        :param commit: The commit to evaluate

        :returns: True if this detector got triggered
        :rtype: bool
        """


class BasePatternBaseDetector(BaseDetector):
    """Check if the commit message respects a pattern"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the detector.

        :param pattern: The pattern to match if it starts with

        :param *args: Check with the base class
        :param **kwargs: Check with the base class
        """
        super(BasePatternBaseDetector, self).__init__(
            *args, **kwargs)

        self._pattern: str = kwargs.get('pattern', None)

    @property
    def pattern(self) -> str:
        """Return pattern value of the detector."""
        return self._pattern

    def validate_detector_params(self) -> NoReturn:
        """Check if all the parameters given to the detector make sens."""
        super(BasePatternBaseDetector, self).validate_detector_params()
        if not isinstance(self._pattern, str):
            raise exception.DetectorValidationException(
                ('Patter: {} is not valid.'
                 'it must be specified and of type string').format(
                     self._pattern))


class BasePatternSimpleComparationDetector(BasePatternBaseDetector):
    """Check if the commit message respects a pattern"""

    def __init__(self, *args: str, **kwargs: Any) -> None:
        """Initialize the detector.

        :param pattern: The pattern to match if it starts with

        :param *args: Check with the base class
        :param **kwargs: Check with the base class
        """
        super(BasePatternSimpleComparationDetector, self).__init__(
            *args, **kwargs)

        self._case_sensitive: bool = kwargs.get('case_sensitive', True)

    @property
    def case_sensitive(self) -> bool:
        """Return case_sensitive value of the detector."""
        return self._case_sensitive

    def validate_detector_params(self) -> NoReturn:
        """Check if all the parameters given to the detector make sens."""
        super(
            BasePatternSimpleComparationDetector,
            self).validate_detector_params()
        if not isinstance(self._case_sensitive, bool):
            raise exception.DetectorValidationException(
                ('case_sensitive: {} is not valid.'
                 'it must be of type bool').format(
                     self._case_sensitive))

    def __prepare_text(self, text: str) -> str:
        """Prepare a text according to the config."""
        if not self._case_sensitive:
            text = text.lower()
        if self._strip:
            text = text.strip()
        return text

    def _prepare_commit_message(self, commit: git.objects.commit.Commit) -> str:
        """Get the prepared commit message according to the config."""
        return self.__prepare_text(commit.message)


class CommitMessageHeadStartsWithDetector(
        BasePatternSimpleComparationDetector):
    """Check if the head of the commit message has a particular pattern."""

    def evaluate(self, commit: git.objects.commit.Commit) -> bool:
        """Check if the commit message head starts with a given string

        :param commit: The commit to evaluate

        :returns: True if this detector got triggered
        :rtype: book
        """
        message = self._prepare_commit_message(commit)

        if self._case_sensitive:
            return message.startswith(self._pattern)
        return message.startswith(self._pattern.lower())


class CommitMessageContainsDetector(BasePatternSimpleComparationDetector):
    """Check if the message of the commit contains a particular pattern."""

    def evaluate(self, commit: git.objects.commit.Commit) -> bool:
        """Check if the commit message contains a given string

        :param commit: The commit to evaluate

        :returns: True if this detector got triggered
        :rtype: book
        """
        message = self._prepare_commit_message(commit)

        if self._case_sensitive:
            return self._pattern in message
        return self._pattern.lower() in message


class CommitMessageMatchesRegexDetector(BasePatternBaseDetector):
    """Check if the message of the commit matches regex pattern."""

    def __init__(self, *args: str, **kwargs: Any) -> None:
        """Initialize the detector.

        :param pattern: The pattern to match if it starts with

        :param *args: Check with the base class
        :param **kwargs: Check with the base class
        """
        super(CommitMessageMatchesRegexDetector, self).__init__(
            *args, **kwargs)

        self._compiled_regex = re.compile(self._pattern)

    def validate_detector_params(self) -> NoReturn:
        """Check if all the parameters given to the detector make sens."""
        super(
            CommitMessageMatchesRegexDetector, self).validate_detector_params()

        if self. _compiled_regex is None:
            raise exception.DetectorValidationException(
                ('Patter: {} is not valid regex.'
                 'it must be specified and compliant').format(self._pattern))

    def evaluate(self, commit: git.objects.commit.Commit) -> bool:
        """Check if the commit message matches a regex pattern

        :param commit: The commit to evaluate

        :returns: True if this detector got triggered
        :rtype: book
        """
        return bool(self._compiled_regex.search(commit.message))


DETECTORS = [
    CommitMessageHeadStartsWithDetector,
    CommitMessageContainsDetector,
    CommitMessageMatchesRegexDetector,
]


def detector_factory(detector_name: str) -> abc.ABCMeta:
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
