#!/usr/bin/env python3
"""
Test simple flows of the AutoTag application
"""
import os

import git
import pytest

from auto_tag import core
# pylint:disable=invalid-name

TEST_DATA_SIMPLE_TAG_PATCH_BUMP = [
    ('0.0.1', '0.0.2'),
    ('0.1.1', '0.1.2'),
    ('1.0.1', '1.0.2'),
]

TEST_DATA_SIMPLE_TAG_PATCH_MINOR = [
    ('0.0.1', '0.1.0'),
    ('0.1.1', '0.2.0'),
    ('1.0.1', '1.1.0'),
]

TEST_DATA_SIMPLE_TAG_PATCH_MAJOR = [
    ('0.0.1', '1.0.0'),
    ('0.1.1', '1.0.0'),
    ('1.0.1', '2.0.0'),
]


def test_simple_flow_no_existing_tag(simple_repo):
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo)

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None)
    autotag.work()
    assert '0.0.1' in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag(existing_tag, next_tag, simple_repo):
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[1])

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None)

    autotag.work()
    assert next_tag in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_MINOR)
def test_simple_flow_existing_tag_minor_bump(
        existing_tag, next_tag, simple_repo_minor_commit):
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo_minor_commit)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[1])

    autotag = core.AutoTag(
        repo=simple_repo_minor_commit,
        branch='master',
        upstream_remotes=None)

    autotag.work()
    assert next_tag in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_MAJOR)
def test_simple_flow_existing_tag_major_bump(
        existing_tag, next_tag, simple_repo_major_commit):
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo_major_commit)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[1])

    autotag = core.AutoTag(
        repo=simple_repo_major_commit,
        branch='master',
        upstream_remotes=None)

    autotag.work()
    assert next_tag in repo.tags


def test_push_to_remote(simple_repo, tmpdir):
    """Test the ability to push to remotes."""
    repo = git.Repo(simple_repo)
    cloned_repo_path = os.path.join(tmpdir, 'cloned-repo')

    cloned_repo = repo.clone(cloned_repo_path)

    autotag = core.AutoTag(
        repo=cloned_repo_path,
        branch='master',
        upstream_remotes=['origin'])
    autotag.work()

    assert '0.0.1' in repo.tags
    assert '0.0.1' in cloned_repo.tags


def test_push_to_multiple_remotes(simple_repo, tmpdir):
    """Test the ability to push to remotes."""
    repo = git.Repo(simple_repo)
    cloned_repo_path = os.path.join(tmpdir, 'cloned-repo')
    second_remote_path = os.path.join(tmpdir, 'second_remote')

    cloned_repo = repo.clone(cloned_repo_path)
    second_remote = git.Repo.init(second_remote_path)

    cloned_repo.create_remote('second_remote', second_remote.common_dir)
    autotag = core.AutoTag(
        repo=cloned_repo_path,
        branch='master',
        upstream_remotes=['origin', 'second_remote'])
    autotag.work()

    assert '0.0.1' in cloned_repo.tags
    assert '0.0.1' in repo.tags
    assert '0.0.1' in second_remote.tags


def test_multiple_commits(simple_repo):
    """Test to see if multiple commits with minor and major impact are handled
       properly."""
    repo = git.Repo(simple_repo)

    for message in [
            'feature(m1): this is a feature it trigger a minor update',
            'fix(m1): a fix is triggering a patch',
            'fix(m1): fix with a breaking change \n BREAKING_CHANGE']:
        file_path = os.path.join(
            repo.working_dir, 'f_{}'.format(message[:4]))
        open(file_path, 'w+').close()
        repo.index.commit(message)

    repo.create_tag(
        '1.2.3',
        ref=list(repo.iter_commits())[1])

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None)
    autotag.work()

    assert '2.0.0' in repo.tags
