#!/usr/bin/env python3
"""
Exception used in the AutoTag project
"""


class BaseAutoTagException(Exception):
    """Base exception for the AutoTag project."""


class DetectorValidationException(BaseAutoTagException):
    """Validation failed on a detector"""


class DetectorNotFound(BaseAutoTagException):
    """Validation failed on a detector"""


class ConfigurationError(BaseAutoTagException):
    """Validation failed on a detector"""


class CantFindBranch(BaseAutoTagException):
    """Can't find a specific branch"""


class UnknowkSearchStrategy(BaseAutoTagException):
    """Invalid search strategy."""
