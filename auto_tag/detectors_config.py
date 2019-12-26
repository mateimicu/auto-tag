#!/usr/bin/env python3
"""
Prepare Detectors based on a file config.
"""
from typing import Any
from typing import Optional
from typing import Union
from typing import List
import logging
import io
import yaml

from auto_tag import exception
from auto_tag import detectors
from auto_tag import constants


# pylint:disable=too-few-public-methods


class DetectorsConfig():
    """Handles instantiation of detectors based on a config file."""

    def __init__(self, data: str, logger: Optional[Any] = None) -> None:
        """Initiate the config."""
        self._data = data
        self._logger = logger or logging.getLogger(__name__)
        self._detectors: Union[List[detectors.BaseDetector], None] = None

    @classmethod
    def from_file(cls, filepath: str, logger: Optional[Any] = None) -> Any:
        """Read config from a file."""
        with open(filepath, 'r') as file_stream:
            return cls(file_stream.read(), logger)

    @classmethod
    def from_default(cls, logger: Optional[Any] = None) -> Any:
        """Return a configuration of the default setting."""
        return cls(constants.DEFAULT_CONFIG_DETECTORS, logger)

    def _parse_detectors(self) -> None:
        """Parse the file and instantiate detectors."""
        self._detectors = []
        stream = io.StringIO(self._data)
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exception.BaseAutoTagException(
                'Can\'t handle config {}'.format(exc))

        if 'detectors' not in data:
            raise exception.ConfigurationError("Can't find key detectors")

        for detector_name, data in data['detectors'].items():
            self._logger.debug('Found detector %s', detector_name)
            if 'type' not in data:
                raise exception.ConfigurationError(
                    'Can\'t find type for detector {}'.format(detector_name))
            detector_class = detectors.detector_factory(data['type'])

            self._logger.debug('Detector %s is %s',
                               detector_name, detector_class)

            if 'produce_type_change' not in data:
                raise exception.ConfigurationError(
                    'Can\'t find produce_type_change for detector {}'.format(
                        detector_name))
            change_type = data['produce_type_change']
            self._logger.debug('Detector %s produces %s',
                               detector_name, change_type)

            extra_args = data.get('params', {})
            self._logger.debug('Detector %s has extra args %s',
                               detector_name, extra_args)
            detector_obj = detector_class(
                name=detector_name, change_type=change_type, **extra_args)

            self._logger.info('Prepared detector %s of type %s -> %s',
                              detector_name, detector_class, change_type)
            self._detectors.append(detector_obj)

    @property
    def detectors(self) -> Union[List[detectors.BaseDetector], None]:  # type: ignore
        """Return list of detectors."""
        if self._detectors is None:
            self._parse_detectors()
        return self._detectors
