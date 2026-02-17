# Maintenance Plan — auto-tag

**Date:** 2026-02-17
**Source:** Consolidated from 5 independent reviews (Database, Architecture, Maintenance, Testing, Security)
**Base branch:** `maintenance/dependency-updates`

---

## Already Addressed

The following issues identified by reviewers have already been resolved on existing branches:

| Finding | Resolved On |
|---|---|
| Remove `six` dependency from setup.py and detectors.py | `maintenance/dependency-updates` (d42f64c) |
| Remove `confuse` dependency from setup.py | `maintenance/dependency-updates` (d42f64c) |
| Update Python classifiers to 3.10/3.11/3.12 | `maintenance/dependency-updates` (8368c1f) |
| Add `python_requires='>=3.10'` | `maintenance/dependency-updates` (8368c1f) |
| Update CI Python matrix to 3.10/3.11 | `fix/ci-update-python-and-actions` (d2a7ac3) |
| Bump pylint/mypy for Python 3.11 compatibility | `fix/ci-update-python-and-actions` (5ebc701) |
| Clean up .pylintrc for pylint 2.17 | `fix/ci-update-python-and-actions` (cb2cf14) |
| Mark mypy as advisory (continue-on-error) | `fix/ci-update-python-and-actions` (202d177) |

---

## Work Packages

### WP1: Critical Security & Runtime Fixes

**Priority:** P0 — Must fix before any release
**Estimated scope:** 3 files changed

| # | Finding | File(s) | Severity | Sources |
|---|---|---|---|---|
| 1 | **GitPython RCE vulnerabilities** — CVE-2024-22190 and CVE-2022-24439. Current pin `>=3.1.18` allows vulnerable versions. | setup.py, Pipfile | CRITICAL | Security |
| 2 | **Syntax error `self. _compiled_regex`** — Extra space between `self.` and `_compiled_regex` causes `AttributeError` at runtime when `validate_detector_params()` is called on a regex detector. | detectors.py:208 | HIGH | Database, Architecture |
| 3 | **Shell command injection in entrypoint.sh** — `sh -c "auto-tag $*"` allows argument injection. | entrypoint.sh | HIGH | Security |

**Actions:**
1. Bump gitpython to `>=3.1.45` in setup.py and Pipfile
2. Fix `self. _compiled_regex` → `self._compiled_regex` in detectors.py:208
3. Replace entrypoint.sh contents with `#!/bin/sh` / `exec auto-tag "$@"`

---

### WP2: Dockerfile Fix

**Priority:** P1 — Broken build artifact
**Estimated scope:** 1 file changed

| # | Finding | File(s) | Severity | Sources |
|---|---|---|---|---|
| 4 | **Wrong package manager** — `apk add git` is Alpine; base image `python:3.9-slim` is Debian. | Dockerfile | HIGH | Maintenance, Security |
| 5 | **Outdated base image** — Should match CI Python version (3.11). | Dockerfile | MEDIUM | Maintenance |

**Actions:**
1. Change base image from `python:3.9-slim` to `python:3.11-slim`
2. Replace `apk add git` with `apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*`

---

### WP3: CI/CD Security Hardening

**Priority:** P1–P2
**Estimated scope:** 3–4 files changed

| # | Finding | File(s) | Severity | Sources |
|---|---|---|---|---|
| 6 | **`pull_request_target` workflow risk** — auto-merge.yaml grants write permissions on PR events, which is a supply-chain risk even with the `dependabot[bot]` actor check. | .github/workflows/auto-merge.yaml | HIGH | Security |
| 7 | **Unpinned GitHub Actions** — `actions/checkout@v4`, `actions/setup-python@v5`, `dependabot/fetch-metadata@v2` should use commit SHA pins. | .github/workflows/*.yml, .github/workflows/*.yaml | MEDIUM | Security |
| 8 | **Deprecated codecov package** — The `codecov` PyPI package is yanked. CI should use `codecov/codecov-action@v4` instead. | .github/workflows/python-ci.yml, Pipfile | MEDIUM | Security |
| 9 | **Unsafe version parsing in publish_docker.sh** — Shell pipeline with `cat | grep | cut | tr` is fragile and could be exploited. | ci/publish_docker.sh | MEDIUM | Security |
| 10 | **Missing workflow permissions blocks** — CI workflow lacks top-level `permissions` restriction. | .github/workflows/python-ci.yml | LOW | Security |

**Actions:**
1. In auto-merge.yaml: restrict to `pull_request_target` types `[labeled, synchronize]` or limit to metadata-only checkout
2. Pin all GitHub Actions to full commit SHAs (with version comment)
3. Remove `codecov` from Pipfile; add `codecov/codecov-action@v4` step in CI workflow
4. In publish_docker.sh: use `python -c "..."` to extract version from setup.py instead of shell pipeline
5. Add top-level `permissions: {}` to python-ci.yml with per-job overrides

---

### WP4: Fix Test Suite

**Priority:** P1 — 60/80 tests currently failing
**Estimated scope:** 3–5 files changed

| # | Finding | File(s) | Severity | Sources |
|---|---|---|---|---|
| 11 | **Git init default branch mismatch** — `git init` defaults to `main` on modern systems but tests assume `master`. This causes 60/80 test failures. | conftest.py:40 | HIGH | Testing, Maintenance |
| 12 | **Hardcoded `master` branch in tests** — 35+ occurrences across test files. Should use a constant or fixture. | test_core.py, test_e2e.py | MEDIUM | Testing, Maintenance |
| 13 | **Deprecated pytest `LocalPath` API** — `from py._path.local import LocalPath` is deprecated and blocks pytest upgrades. | conftest.py:15 | MEDIUM | Maintenance |
| 14 | **Unimplemented test stub** — Empty test at test_core.py:143. | test_core.py:143 | LOW | Architecture, Maintenance, Testing |
| 15 | **Missing pytest configuration** — No pytest.ini/pyproject.toml `[tool.pytest]`, no coverage thresholds, no test markers. | (new) pytest.ini or pyproject.toml | MEDIUM | Testing |

**Actions:**
1. In conftest.py:40: change `git.Repo.init(repo_path)` to `git.Repo.init(repo_path, initial_branch='master')`
2. Define `DEFAULT_BRANCH = 'master'` constant in conftest.py; replace all hardcoded `'master'` references in test files
3. Replace `from py._path.local import LocalPath` with `pathlib.Path`; update fixture type hints (`tmpdir: LocalPath` → `tmp_path: pathlib.Path`)
4. Either implement the test stub at test_core.py:143 or remove it
5. Add `[tool.pytest.ini_options]` section (or pytest.ini) with coverage threshold and markers

---

### WP5: Code Quality & Bug Fixes

**Priority:** P1–P2
**Estimated scope:** 4–5 files changed

| # | Finding | File(s) | Severity | Sources |
|---|---|---|---|---|
| 16 | **Incorrect `NoReturn` type hints** — `validate_detector_params()` methods use `NoReturn` return type but they return normally (only raise on error). Should be `None`. | detectors.py:58,98,129,204 | MEDIUM | Architecture |
| 17 | **Silent failure in `get_remote()`** — Returns `None` instead of raising when remote not found, despite the return type annotation implying non-None. | core.py:130–135 | MEDIUM | Architecture |
| 18 | **No error handling for git operations** — `repo.create_tag()` at core.py:207 and `remote.push()` at core.py:149 can raise but are uncaught. | core.py:207–211, core.py:149 | HIGH | Architecture |
| 19 | **Context manager `__enter__` doesn't return self** — `GitCustomeEnvironment.__enter__` returns `None`, so `with ... as ctx` would be `None`. | git_custom_env.py:30 | LOW | Architecture |
| 20 | **Generic exception wrapping** — `detectors_config.py:48` catches `yaml.YAMLError` but re-raises as generic `BaseAutoTagException`, losing the exception chain. | detectors_config.py:46–49 | MEDIUM | Database, Architecture |
| 21 | **Git config race condition** — `GitCustomeEnvironment` modifies `.git/config` directly instead of using environment variables. Concurrent operations could conflict. | git_custom_env.py | MEDIUM | Database |

**Actions:**
1. Change `NoReturn` to `None` on all `validate_detector_params()` return types
2. Update `get_remote()` return type to `Optional[git.remote.Remote]` (or raise on missing remote — determine preferred approach)
3. Wrap `repo.create_tag()` and `remote.push()` in try/except with meaningful error messages
4. Add `return self` to `__enter__` method
5. Use `raise ... from exc` syntax in detectors_config.py to preserve exception chain
6. Consider refactoring `GitCustomeEnvironment` to use `GIT_COMMITTER_NAME`/`GIT_COMMITTER_EMAIL` environment variables instead of config file mutation (or document the limitation)

---

### WP6: Naming, Typo, and Documentation Cleanup

**Priority:** P3
**Estimated scope:** 8–10 files changed

| # | Finding | File(s) | Severity | Sources |
|---|---|---|---|---|
| 22 | **Class name typos** — `GitCustomeEnvironment` (git_custom_env.py:11) and `UnknowkSearchStrategy` (tag_search_strategy.py exception class). | git_custom_env.py, tag_search_strategy.py, core.py, exception.py | LOW | Database, Architecture |
| 23 | **Code/doc typos** — "Initializa" (core.py:35), "informations" (core.py:157), ":rtype: book" (detectors.py:161,179,219), "Exampels", "decimation process". | Multiple | LOW | Maintenance |
| 24 | **Trailing tab in setup.py** — `author_email` field has trailing tab character. | setup.py:26 | LOW | Maintenance |
| 25 | **Missing SECURITY.md** — No security policy for vulnerability reporting. | (new) SECURITY.md | LOW | Security |
| 26 | **Outdated default branch in CLI** — `cli.py:16` defaults to `'master'`. | cli.py:16 | LOW | Architecture |

**Actions:**
1. Rename `GitCustomeEnvironment` → `GitCustomEnvironment` (update all references in core.py, tests)
2. Rename `UnknowkSearchStrategy` → `UnknownSearchStrategy` (update exception.py and tag_search_strategy.py)
3. Fix docstring typos across identified files
4. Remove trailing tab from setup.py:26
5. Add SECURITY.md with vulnerability reporting instructions
6. Consider updating default branch to `'main'` in cli.py (coordinate with repo settings)

**Note:** Class renames are breaking changes for any code importing these names directly. Since these are internal classes and the package is <1.0, this is acceptable.

---

### WP7: Test Architecture Improvements

**Priority:** P3
**Estimated scope:** 3–5 files changed

| # | Finding | File(s) | Severity | Sources |
|---|---|---|---|---|
| 27 | **Massive test duplication** — test_core.py (569 lines) and test_e2e.py (390 lines) have ~90% overlap. Only 3 unique tests in test_core.py. | test_core.py, test_e2e.py | HIGH (maintenance burden) | Testing |
| 28 | **Coverage gaps** — `__main__.py` at 0%, `entrypoint.py` and `cli.py` partial. Overall 79.14% vs 85% target. | Multiple | MEDIUM | Testing |
| 29 | **Duplicate entry points** — Both `__main__.py` and `entrypoint.py` exist, unclear which is canonical. | __main__.py, entrypoint.py | LOW | Architecture |

**Actions:**
1. Analyze exact overlap between test_core.py and test_e2e.py; consolidate shared tests into a common base or parameterized fixtures
2. Add tests for `__main__.py`, improve `cli.py` coverage
3. Determine canonical entry point and remove or clearly document the other

---

### WP8: Modernization (Future)

**Priority:** P3 — Nice to have, no urgency
**Estimated scope:** Varies

| # | Finding | File(s) | Severity | Sources |
|---|---|---|---|---|
| 30 | **Migrate to pyproject.toml** — Currently uses legacy setup.py. Coordinate with issue #298. | setup.py → pyproject.toml | LOW | Maintenance |
| 31 | **Modern type hints** — `typing.List` → `list`, `typing.Optional[X]` → `X \| None` (Python 3.10+). | Multiple | LOW | Architecture |
| 32 | **f-string migration** — 12+ `.format()` calls and some `%` formatting. | Multiple | LOW | Maintenance, Architecture |
| 33 | **Unbounded commit iteration** — `repo.iter_commits()` has no `max_count`, could be slow on large repos. | core.py:111, tag_search_strategy.py:66 | LOW | Database |
| 34 | **Stale remote branches** — 40+ old branches on origin. | (git operation) | LOW | Maintenance |
| 35 | **Add .editorconfig** — No editor configuration for consistent formatting. | (new) .editorconfig | LOW | Maintenance |
| 36 | **Protected member access** — `logging._nameToLevel` in cli.py:23–26 is a private API. | cli.py:23–26 | LOW | Architecture |
| 37 | **Stale Pipfile.lock** — Contains yanked packages. Regenerate after dependency updates. | Pipfile.lock | HIGH | Maintenance |
| 38 | **Add Python 3.12 to CI matrix** — Classifiers claim 3.12 support but CI only tests 3.10/3.11. | .github/workflows/python-ci.yml | LOW | Maintenance |

---

## Recommended Execution Order

```
WP1 (Critical Security)
 │
 ├──► WP2 (Dockerfile)          — independent
 ├──► WP3 (CI/CD Hardening)     — independent
 └──► WP4 (Fix Test Suite)      — independent
       │
       └──► WP5 (Code Quality)  — benefits from working tests
             │
             └──► WP6 (Naming/Typos)    — benefits from stable code
                   │
                   └──► WP7 (Test Architecture) — after code is stable
                         │
                         └──► WP8 (Modernization) — last, lowest risk
```

WP1 must land first. WP2, WP3, and WP4 can proceed in parallel after WP1. WP5 through WP8 are sequential as each builds on the stability established by the previous.

---

## Cross-Cutting Concerns

1. **Pipfile.lock regeneration** (WP8 #37) should happen after WP1 (gitpython bump) and WP3 (codecov removal) to avoid regenerating twice.
2. **pyproject.toml migration** (WP8 #30) should coordinate with GitHub issue #298 and happen after all setup.py changes are complete.
3. **Class renames in WP6** will require updating imports in test files — coordinate with WP4/WP7 test changes to avoid merge conflicts.
4. **Python 3.12 CI addition** (WP8 #38) should happen after WP4 (test fixes) to avoid running a broken test suite on yet another Python version.

---

## Summary

| Priority | Work Packages | Findings |
|---|---|---|
| P0 (Critical) | WP1 | 3 |
| P1 (High) | WP2, WP3 (partial), WP4 (partial), WP5 (partial) | 10 |
| P2 (Medium) | WP3 (partial), WP4 (partial), WP5 (partial) | 10 |
| P3 (Low) | WP6, WP7, WP8 | 15 |
| **Total unique findings** | | **38** |
| **Already resolved** | | **8** |
| **Net remaining** | | **38** |

38 unique findings consolidated from 5 reviewer reports (after de-duplicating overlapping findings across reports). 8 additional issues were already addressed on existing branches.
