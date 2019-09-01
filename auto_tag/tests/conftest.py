#!/usr/bin/env python3
"""
Fixtures used to test AutoTag module.
"""
import os

import git
import pytest

from auto_tag import detectors_config


@pytest.fixture
def simple_repo(tmpdir):
    """Return a simple repository with 3 basic commits and no tags."""
    bare_repo_path = os.path.join(tmpdir, 'bare-repo')
    bare_repo = git.Repo.init(bare_repo_path, bare=True)

    for commit_id in range(3):
        file_path = os.path.join(
            tmpdir, 'bare-repo', 'f_{}'.format(str(commit_id)))
        commit_text = 'commit #{}'.format(str(commit_id))
        open(file_path, 'w+').close()
        bare_repo.index.commit(commit_text)

    return bare_repo_path


@pytest.fixture
def default_detectors():
    """Return a simple repository with 3 basic commits and no tags."""
    config = detectors_config.DetectorsConfig.from_default()
    return config.detectors


@pytest.fixture
def simple_repo_minor_commit(simple_repo):
    """Return a simple repository with 3 basic commits and no tags."""
    bare_repo = git.Repo(simple_repo)

    file_path = os.path.join(simple_repo, 'f_{}'.format('minor'))
    commit_text = 'feature(minor): this must trigger a minor change'
    open(file_path, 'w+').close()
    bare_repo.index.commit(commit_text)

    return simple_repo


@pytest.fixture
def simple_repo_major_commit(simple_repo):
    """Return a simple repository with 3 basic commits and no tags."""
    bare_repo = git.Repo(simple_repo)

    file_path = os.path.join(simple_repo, 'f_{}'.format('minor'))
    commit_text = 'this must trigger a minor change \n BREAKING_CHANGE'
    open(file_path, 'w+').close()
    bare_repo.index.commit(commit_text)

    return simple_repo
