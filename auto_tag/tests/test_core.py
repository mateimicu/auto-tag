#!/usr/bin/env python3
"""
Test simple flows of the AutoTag application
"""
import os

import git
import pytest

from auto_tag import core
from auto_tag.detectors import CommitMessageContainsDetector
from auto_tag.detectors import CommitMessageHeadStartsWithDetector
from typing import List
from typing import Union
from py._path.local import LocalPath
# pylint:disable=invalid-name

BIG_TAG = '100.100.100'

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
TEST_NAME = 'test_user'
TEST_EMAIL = 'test@email.com'

TEST_NAME_2 = 'test_user_2'
TEST_EMAIL_2 = 'test_2@email.com'


def test_simple_flow_no_existing_tag(simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test a simple flow.

    Scenario:
        A repository with a few commits but no tag.
    Outcome:
        Tag 0.0.1 should be created.

    """
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)
    autotag.work()
    assert '0.0.1' in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag_and_extra_tag_on_separate_branch(
        existing_tag: str, next_tag: str, simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test to see if only specified branch is evaluated.

    Idea:
        If we already have tags on a another branch (let's say `new_branch`)
        if we want to auto-tag branch `master` then we should only look
        at tags on this branch.
    Scenario:
        Branch `master` has `current_tag` and `new_branch` has tag `BIG_TAG`.
        `BIG_TAG` is bigger then `current_tag`.
    Output:
        When we auto-tag the `master` branch then it should apply `next_tag`
    """
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[-1])

    # create a bigger tag on a new branch
    new_branch = repo.create_head('new_branch', force=True)
    repo.head.reference = new_branch
    # repo.head.reset(index=False, working_tree=False)

    file_path = os.path.join(simple_repo, 'extra_file')
    commit_text = 'commit an extra file'
    open(file_path, 'w+').close()
    extra_commit = repo.index.commit(commit_text)
    repo.create_tag(BIG_TAG, extra_commit)

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)

    autotag.work()
    assert next_tag in repo.tags


# pylint: disable=unused-argument, fixme
@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag_and_tag_exists_on_another_branch(
        existing_tag: str, next_tag: str, simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test to see if only specified branch is evaluated.

    Idea:
        If we already have tags on a dolerite branch (let's say `new_branch`)
        if we want to auto-tag branch `master` then we should only look
        at tags on this branch.
    Scenario:
        Branch `master` has `current_tag` and `new_branch` has tag
        `next_tag`.
        `next_tag` is bigger then `current_tag`.
    Output:
        When we auto-tag the `master` branch then it should throw an error
        because we can't have two tags with the same name.
    """
    # TODO(mmicu): to be implemented
    assert True


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag(
        existing_tag: str, next_tag: str, simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[-1])

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)

    autotag.work()
    assert next_tag in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag_mixed_tags(
        existing_tag: str, next_tag: str, simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        'v'+existing_tag,
        ref=list(repo.iter_commits())[-1])

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)

    autotag.work()
    assert next_tag in repo.tags


def test_simple_flow_existing_tag_mixed_tag(simple_repo: str,
                                            default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test the support for mixed tags."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        '2.0.1',
        ref=list(repo.iter_commits())[0])

    repo.create_tag(
        'v2.0.1',
        ref=list(repo.iter_commits())[0])

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)

    autotag.work()
    assert '2.0.2' in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag_on_last_commit(
        existing_tag: str, next_tag: str, simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[0])

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL,
        skip_if_exists=True)

    autotag.work()
    assert next_tag not in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag_append_v(
        existing_tag: str, next_tag: str, simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[-1])

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL,
        append_v=True)

    autotag.work()
    assert 'v{}'.format(next_tag) in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_MINOR)
def test_simple_flow_existing_tag_minor_bump(
        existing_tag: str, next_tag: str, simple_repo_minor_commit: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo_minor_commit, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[-1])

    autotag = core.AutoTag(
        repo=simple_repo_minor_commit,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)

    autotag.work()
    assert next_tag in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_MAJOR)
def test_simple_flow_existing_tag_major_bump(
        existing_tag: str, next_tag: str, simple_repo_major_commit: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo_major_commit, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[-1])

    autotag = core.AutoTag(
        repo=simple_repo_major_commit,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)

    autotag.work()
    assert next_tag in repo.tags


def test_push_to_remote(simple_repo: str, tmpdir: LocalPath, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test the ability to push to remotes."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    cloned_repo_path = os.path.join(tmpdir, 'cloned-repo')

    cloned_repo = repo.clone(cloned_repo_path)

    autotag = core.AutoTag(
        repo=cloned_repo_path,
        branch='master',
        upstream_remotes=['origin'],
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)
    autotag.work()

    assert '0.0.1' in repo.tags
    assert '0.0.1' in cloned_repo.tags


def test_push_to_multiple_remotes(simple_repo: str, tmpdir: LocalPath, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test the ability to push to remotes."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    cloned_repo_path = os.path.join(tmpdir, 'cloned-repo')
    second_remote_path = os.path.join(tmpdir, 'second_remote')

    cloned_repo = repo.clone(cloned_repo_path)
    second_remote = git.Repo.init(second_remote_path, odbt=git.GitDB)

    cloned_repo.create_remote('second_remote', second_remote.common_dir)
    autotag = core.AutoTag(
        repo=cloned_repo_path,
        branch='master',
        upstream_remotes=['origin', 'second_remote'],
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)
    autotag.work()

    assert '0.0.1' in cloned_repo.tags
    assert '0.0.1' in repo.tags
    assert '0.0.1' in second_remote.tags


def test_multiple_commits(simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test to see if multiple commits with minor and major impact are handled
       properly."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

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
        ref=list(repo.iter_commits())[-1])

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)
    autotag.work()

    assert '2.0.0' in repo.tags


def test_tag_message_has_heading(simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        '1.2.3',
        ref=list(repo.iter_commits())[0])

    messages = [
        'feature(m1): this is a feature it trigger a minor update \n text',
        'fix(m1): a fix is triggering a patch \n more text',
        'fix(m1): with a breaking change \n BREAKING_CHANGE \n even more'
    ]
    for message in messages:
        file_path = os.path.join(
            repo.working_dir, 'f_{}'.format(message[:4]))
        open(file_path, 'w+').close()
        repo.index.commit(message)

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)
    autotag.work()

    assert '2.0.0' in repo.tags
    for message in messages:
        assert message.split('\n')[0].strip() in repo.tags['2.0.0'].tag.message


def test_tag_message_user_exists_and_not_specified(
        simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    with repo.config_writer() as config_writer:
        config_writer.set_value('user', 'name', TEST_NAME)
        config_writer.set_value('user', 'email', TEST_EMAIL)

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        upstream_remotes=None,
        detectors=default_detectors,
        git_name=TEST_NAME,
        git_email=TEST_EMAIL)
    autotag.work()
    assert '0.0.1' in repo.tags
    assert TEST_NAME == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL == repo.tags['0.0.1'].tag.tagger.email


def test_tag_message_user_exists_and_specified(simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    with repo.config_writer() as config_writer:
        config_writer.set_value('user', 'name', TEST_NAME)
        config_writer.set_value('user', 'email', TEST_EMAIL)

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        detectors=default_detectors,
        git_name=TEST_NAME_2,
        git_email=TEST_EMAIL_2,
        upstream_remotes=None)
    autotag.work()
    assert '0.0.1' in repo.tags
    assert TEST_NAME_2 == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL_2 == repo.tags['0.0.1'].tag.tagger.email


def test_tag_message_user_exists_and_only_email_specified(
        simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    with repo.config_writer() as config_writer:
        config_writer.set_value('user', 'name', TEST_NAME)
        config_writer.set_value('user', 'email', TEST_EMAIL)

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        detectors=default_detectors,
        git_email=TEST_EMAIL_2,
        upstream_remotes=None)
    autotag.work()
    assert '0.0.1' in repo.tags
    assert TEST_NAME == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL_2 == repo.tags['0.0.1'].tag.tagger.email


def test_tag_message_user_does_not_exists_and_specified(
        simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        detectors=default_detectors,
        git_name=TEST_NAME_2,
        git_email=TEST_EMAIL_2,
        upstream_remotes=None)
    autotag.work()
    assert '0.0.1' in repo.tags
    assert TEST_NAME_2 == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL_2 == repo.tags['0.0.1'].tag.tagger.email


def test_tag_message_user_exists_and_specify_make_sure_clean_env(
        simple_repo: str, default_detectors: List[Union[CommitMessageContainsDetector, CommitMessageHeadStartsWithDetector]]) -> None:
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    with repo.config_writer() as config_writer:
        config_writer.set_value('user', 'name', TEST_NAME)
        config_writer.set_value('user', 'email', TEST_EMAIL)

    autotag = core.AutoTag(
        repo=simple_repo,
        branch='master',
        detectors=default_detectors,
        git_email=TEST_EMAIL_2,
        upstream_remotes=None)
    autotag.work()
    assert '0.0.1' in repo.tags
    assert TEST_NAME == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL_2 == repo.tags['0.0.1'].tag.tagger.email

    with repo.config_writer() as config_writer:
        repo_config_name = config_writer.get_value('user', 'name')
        repo_config_email = config_writer.get_value('user', 'email')

    assert TEST_NAME == repo_config_name
    assert TEST_EMAIL == repo_config_email
