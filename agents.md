# Agent Guidelines for auto-tag

This document provides guidelines for AI agents working on this codebase.

## Project Overview

**auto-tag** is a Python CLI tool that automatically creates semantic version tags on git branches based on commit message patterns. It analyzes commit messages using configurable detectors and bumps the version accordingly (MAJOR, MINOR, PATCH).

### Architecture

```
auto_tag/
├── __main__.py      # Entry point (calls main from entrypoint)
├── entrypoint.py    # Main entry point, wires CLI to core
├── cli.py           # Argument parser
├── core.py          # AutoTag class - main business logic
├── detectors.py     # Commit message pattern detectors
├── detectors_config.py  # YAML config loading for detectors
├── constants.py     # Change types, search strategies
├── tag_search_strategy.py  # Strategies for finding latest tag
├── git_custom_env.py  # Git environment context manager
├── exception.py     # Custom exceptions
└── tests/           # Test suite
    ├── conftest.py  # Pytest fixtures
    ├── test_core.py
    ├── test_detectors.py
    ├── test_detectors_config.py
    ├── test_tag_search_strategy.py
    └── test_e2e.py
```

### Key Concepts

- **Detectors**: Classes that evaluate commit messages and determine change type
  - `CommitMessageHeadStartsWithDetector`
  - `CommitMessageContainsDetector`
  - `CommitMessageMatchesRegexDetector`
- **Change Types**: MAJOR (100), MINOR (10), PATCH (1) - highest wins
- **Search Strategies**: How to find the latest tag (biggest/latest in repo/branch)

---

## TDD Workflow (Required)

**All changes MUST follow Test-Driven Development:**

1. **Write a failing test first**
   - Create a test that describes the expected behavior
   - Run the test to verify it fails
   - Commit: "test: add test for <feature>"

2. **Write minimal code to pass**
   - Implement just enough to make the test pass
   - No extra features or "nice to haves"

3. **Refactor if needed**
   - Clean up while keeping tests green
   - Run full test suite after refactoring

4. **Verify all tests pass before committing**

### Example TDD Cycle

```bash
# 1. Write test, verify it fails
pytest auto_tag/tests/test_detectors.py::test_new_detector -v
# Expected: FAILED

# 2. Implement feature
# ... edit code ...

# 3. Verify test passes
pytest auto_tag/tests/test_detectors.py::test_new_detector -v
# Expected: PASSED

# 4. Run full suite
pytest auto_tag/tests/ -v
# Expected: All PASSED
```

---

## Running Tests

### Setup Environment

```bash
# Install dependencies using pip with pyproject.toml
pip install -e ".[dev]"

# Or using pipenv (legacy)
pipenv install --dev
pipenv shell
```

### Test Commands

```bash
# Run all tests
pytest auto_tag/tests/ -v

# Run with coverage
pytest auto_tag/tests/ --cov=auto_tag

# Run specific test file
pytest auto_tag/tests/test_core.py -v

# Run specific test
pytest auto_tag/tests/test_core.py::test_function_name -v

# Run tests matching pattern
pytest auto_tag/tests/ -k "detector" -v
```

### Linting and Type Checking

```bash
# Run ruff (linting and formatting)
ruff check auto_tag
ruff format --check auto_tag

# Run mypy (type checking)
mypy auto_tag
```

---

## Code Style Conventions

### Python Style

- Python 3.9+ compatible code
- Use type hints for all function signatures
- Use `abc.ABC` for abstract base classes
- Use `pathlib.Path` instead of `os.path` where possible
- Use f-strings for string formatting

### Naming

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private attributes: `_leading_underscore`

### Documentation

- All public classes and methods need docstrings
- Use Google-style docstrings:

```python
def function(param: str) -> bool:
    """Short description.

    :param param: Description of parameter
    :returns: Description of return value
    :rtype: bool
    """
```

---

## Making Changes

### Before Starting

1. Read existing tests for the area you're modifying
2. Understand the current behavior
3. Check if similar patterns exist in the codebase

### Change Workflow

1. Create/update tests first (TDD)
2. Make minimal changes to pass tests
3. Run the full test suite
4. Run linting and type checking
5. Commit with conventional commit message

### Commit Messages

Use conventional commits:
- `feat:` new feature (MINOR bump)
- `fix:` bug fix (PATCH bump)
- `test:` adding/updating tests
- `refactor:` code change that neither fixes nor adds
- `docs:` documentation only
- `chore:` maintenance tasks

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `auto_tag/core.py` | Main `AutoTag` class with tagging logic |
| `auto_tag/detectors.py` | Pattern matching for commit messages |
| `auto_tag/cli.py` | CLI argument parsing |
| `auto_tag/constants.py` | Change types, default config |
| `auto_tag/tests/conftest.py` | Shared test fixtures |
| `pyproject.toml` | Project config, dependencies, tool settings |
| `.github/workflows/python-ci.yml` | CI pipeline |

---

## Common Tasks

### Adding a New Detector

1. Write test in `test_detectors.py`
2. Create class inheriting from `BasePatternBaseDetector` or `BaseDetector`
3. Implement `evaluate()` method
4. Add to `DETECTORS` list in `detectors.py`
5. Verify tests pass

### Modifying Tag Search Strategy

1. Write test in `test_tag_search_strategy.py`
2. Add strategy function to `tag_search_strategy.py`
3. Add constant to `constants.py` if new strategy name
4. Update CLI choices if needed
