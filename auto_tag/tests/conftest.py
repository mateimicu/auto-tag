#!/usr/bin/env python3
"""
Fixtures used to test AutoTag module.
"""
import time
from email.utils import formatdate
from pathlib import Path
from typing import Iterable

import git
import pytest

from auto_tag import detectors_config
from auto_tag import detectors

BRANCH_NAME_A = 'branch_a'
BRANCH_NAME_B = 'branch_b'

TAGS = {
    BRANCH_NAME_A: [
        '0.0.1',
        '1.0.1',
        '0.1.1',
    ],
    BRANCH_NAME_B: [
        '1.1.1',
    ]
}


@pytest.fixture
def simple_repo(tmp_path: Path) -> str:
    """Return a simple repository with 3 basic commits and no tags."""
    repo_path = tmp_path / 'test-repo'
    repo = git.Repo.init(str(repo_path), initial_branch='master')

    for commit_id in range(3):
        file_path = repo_path / f'f_{commit_id}'
        file_path.touch()
        repo.index.commit(f'commit #{commit_id}')

    return str(repo_path)


@pytest.fixture
def default_detectors() -> Iterable[detectors.BaseDetector]:
    """Return a simple repository with 3 basic commits and no tags."""
    config = detectors_config.DetectorsConfig.from_default()
    return config.detectors


@pytest.fixture
def simple_repo_minor_commit(simple_repo: str) -> str:
    """Return a simple repository with 3 basic commits and no tags."""
    repo = git.Repo(simple_repo)
    repo_path = Path(simple_repo)

    file_path = repo_path / 'f_minor'
    file_path.touch()
    repo.index.commit('feature(minor): this must trigger a minor change')

    return simple_repo


@pytest.fixture
def simple_repo_major_commit(simple_repo: str) -> str:
    """Return a simple repository with 3 basic commits and no tags."""
    repo = git.Repo(simple_repo)
    repo_path = Path(simple_repo)

    file_path = repo_path / 'f_major'
    file_path.touch()
    repo.index.commit('this must trigger a minor change \n BREAKING_CHANGE')

    return simple_repo


@pytest.fixture
def simple_repo_two_branches(simple_repo: str) -> str:
    """Return a repository with two branches."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo_path = Path(simple_repo)
    # NOTE(mmicu): because we only have seconds granularity
    # we specifically add on second to every commit_date
    commit_date = int(time.time())

    # create branches
    for branch_name in ('branch_a', 'branch_b'):
        current = repo.create_head(branch_name)
        current.checkout()

        for tag in TAGS[branch_name]:
            file_path = repo_path / f'f_{branch_name}_{tag}'
            file_path.touch()

            commit = repo.index.commit(
                f'random commit for {branch_name} {tag}',
                commit_date=formatdate(commit_date))
            commit_date += 1
            repo.create_tag(tag, ref=commit)

    return simple_repo
