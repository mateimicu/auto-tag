#!/usr/bin/env python3
"""
Exception used in the AutoTag project
"""


class BaseAutoTagException(Exception):
    """Base exception for the AutoTag project."""


class DetectorValidationException(BaseAutoTagException):
    """Validation failed on a detector"""
