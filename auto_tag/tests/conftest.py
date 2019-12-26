#!/usr/bin/env python3
"""
Fixtures used to test AutoTag module.
"""
import os
import time
from email.utils import formatdate

import git
import pytest

from auto_tag import detectors_config
from auto_tag import detectors
from typing import Iterator
from py._path.local import LocalPath
from typing import List
from typing import Union

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
def simple_repo(tmpdir: LocalPath) -> str:
    """Return a simple repository with 3 basic commits and no tags."""
    repo_path = os.path.join(tmpdir, 'test-repo')
    repo = git.Repo.init(repo_path)

    for commit_id in range(3):
        file_path = os.path.join(
            tmpdir, 'test-repo', 'f_{}'.format(str(commit_id)))
        commit_text = 'commit #{}'.format(str(commit_id))
        open(file_path, 'w+').close()
        repo.index.commit(commit_text)

    return repo_path


@pytest.fixture
def default_detectors() -> List[detectors.BaseDetector]:
    """Return a simple repository with 3 basic commits and no tags."""
    config = detectors_config.DetectorsConfig.from_default()
    return config.detectors


@pytest.fixture
def simple_repo_minor_commit(simple_repo: str) -> str:
    """Return a simple repository with 3 basic commits and no tags."""
    repo = git.Repo(simple_repo)

    file_path = os.path.join(simple_repo, 'f_{}'.format('minor'))
    commit_text = 'feature(minor): this must trigger a minor change'
    open(file_path, 'w+').close()
    repo.index.commit(commit_text)

    return simple_repo


@pytest.fixture
def simple_repo_major_commit(simple_repo: str) -> str:
    """Return a simple repository with 3 basic commits and no tags."""
    repo = git.Repo(simple_repo)

    file_path = os.path.join(simple_repo, 'f_{}'.format('minor'))
    commit_text = 'this must trigger a minor change \n BREAKING_CHANGE'
    open(file_path, 'w+').close()
    repo.index.commit(commit_text)

    return simple_repo


@pytest.fixture
def simple_repo_two_branches(simple_repo: str) -> str:
    """Return a repository with two branches."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    # NOTE(mmicu): because we only have seconds granularity
    # we specifically add on second to every commit_date
    commit_date = int(time.time())

    # create branches
    for branch_name in ('branch_a', 'branch_b'):
        current = repo.create_head(branch_name)
        current.checkout()

        for tag in TAGS[branch_name]:
            file_path = os.path.join(simple_repo, 'f_{}_{}'.format(
                branch_name, tag))
            commit_text = 'random commit for {} {}'.format(
                branch_name, tag)
            open(file_path, 'w+').close()

            commit = repo.index.commit(
                commit_text, commit_date=formatdate(commit_date))
            commit_date += 1
            repo.create_tag(tag, ref=commit)

    return simple_repo
