#!/usr/bin/env python3
"""
Test simple flows of the AutoTag application
"""

import os

import git
import pytest

from auto_tag import detectors, exception

# pylint:disable=invalid-name

TEST_DATA_REGEX_DETECTOR = [
    ("[a-zA-Z]*[1-9]", "this message has interesting pattern123", True),
    ("[a-zA-Z]*[1-9]", "this message has interesting pattern", False),
]


def test_factory_detector_happy_flow() -> None:
    """Test to see if the factory returns what we expect."""
    assert (
        detectors.detector_factory("CommitMessageContainsDetector")
        == detectors.CommitMessageContainsDetector
    )


def test_factory_detector_no_existing_detector() -> None:
    """Test to see if the factory raises an exception
    for a non existing detector."""
    with pytest.raises(exception.DetectorNotFound):
        assert detectors.detector_factory("NOT_EXISTING_DETECTOR")


def test_CommitMessageHeadStartsWithDetector_validation_type() -> None:
    """Check the validation for the detector."""
    detector = detectors.CommitMessageHeadStartsWithDetector(
        "name", "MAJOR", pattern="test-pattern"
    )
    assert detector.validate_detector_params() is None


def test_CommitMessageHeadStartsWithDetector_invalid_type() -> None:
    """Check to see if the detectors validate the change_type."""
    detector = detectors.CommitMessageHeadStartsWithDetector(
        "name", "BAD_CHANGE_TYPE", pattern="test-pattern"
    )
    with pytest.raises(exception.DetectorValidationException):
        assert detector.validate_detector_params()


def test_CommitMessageHeadStartsWithDetector_invalid_pattern() -> None:
    """Check to see if the detectors validate the pattern."""
    detector = detectors.CommitMessageHeadStartsWithDetector("name", "BAD_CHANGE_TYPE", pattern=[])
    with pytest.raises(exception.DetectorValidationException):
        assert detector.validate_detector_params()


def test_CommitMessageHeadStartsWithDetector_trigger(simple_repo: str) -> None:
    """Check the happy flow of the trigger."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    pattern = "abcd"
    message = pattern + " extra text"
    file_path = os.path.join(repo.working_dir, "dummy_file")
    open(file_path, "w+").close()
    commit = repo.index.commit(message)

    detector = detectors.CommitMessageHeadStartsWithDetector("name", "MAJOR", pattern=pattern)
    assert detector.evaluate(commit)


def test_CommitMessageHeadStartsWithDetector_not_trigger(simple_repo: str) -> None:
    """Check to see if the detector avoids miss matches."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    pattern = "abcd"
    message = "extra text" + pattern + " extra text"
    file_path = os.path.join(repo.working_dir, "dummy_file")
    open(file_path, "w+").close()
    commit = repo.index.commit(message)

    detector = detectors.CommitMessageHeadStartsWithDetector("name", "MAJOR", pattern=pattern)
    assert not detector.evaluate(commit)


def test_CommitMessageHeadStartsWithDetector_trigger_strip(simple_repo: str) -> None:
    """Check the strip functionality."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    pattern = "abcd"
    message = "  \n\n " + pattern + " extra text"
    file_path = os.path.join(repo.working_dir, "dummy_file")
    open(file_path, "w+").close()
    commit = repo.index.commit(message)

    detector = detectors.CommitMessageHeadStartsWithDetector("name", "MAJOR", pattern=pattern)
    assert detector.evaluate(commit)

    detector_no_strip = detectors.CommitMessageHeadStartsWithDetector(
        "name", "MAJOR", pattern=pattern, strip=False
    )
    assert not detector_no_strip.evaluate(commit)


def test_CommitMessageHeadStartsWithDetector_trigger_case(simple_repo: str) -> None:
    """Validate the case sensitivity functionality."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    pattern = "Abcd"
    message = pattern + " extra text"
    file_path = os.path.join(repo.working_dir, "dummy_file")
    open(file_path, "w+").close()
    commit = repo.index.commit(message)

    detector = detectors.CommitMessageHeadStartsWithDetector("name", "MAJOR", pattern=pattern)
    assert detector.evaluate(commit)

    detector_bad_pattern = detectors.CommitMessageHeadStartsWithDetector(
        "name", "MAJOR", pattern=pattern.lower()
    )
    assert not detector_bad_pattern.evaluate(commit)

    detector_insesitive = detectors.CommitMessageHeadStartsWithDetector(
        "name", "MAJOR", pattern=pattern.lower(), case_sensitive=False
    )
    assert detector_insesitive.evaluate(commit)


def test_CommitMessageContainsDetector_trigger(simple_repo: str) -> None:
    """Check the happy flow of the trigger."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    pattern = "abcd"
    message = "extra text" + pattern + " extra text"
    file_path = os.path.join(repo.working_dir, "dummy_file")
    open(file_path, "w+").close()
    commit = repo.index.commit(message)

    detector = detectors.CommitMessageContainsDetector("name", "MAJOR", pattern=pattern)
    assert detector.evaluate(commit)


@pytest.mark.parametrize("pattern, message, expected", TEST_DATA_REGEX_DETECTOR)
def test_CommitMessageMatchesRegexDetector_trigger(
    pattern: str, message: str, expected: bool, simple_repo: str
) -> None:
    """Check the happy flow of the trigger."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    file_path = os.path.join(repo.working_dir, "dummy_file")
    open(file_path, "w+").close()
    commit = repo.index.commit(message)

    detector = detectors.CommitMessageMatchesRegexDetector("name", "MAJOR", pattern=pattern)
    assert detector.evaluate(commit) == expected
