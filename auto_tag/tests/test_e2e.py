#!/usr/bin/env python3
"""
Test simple flows E2E
"""
import os

import git
import pytest

from auto_tag import entrypoint
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


def test_simple_flow_no_existing_tag(simple_repo):
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL]
    )
    assert '0.0.1' in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag(
        existing_tag, next_tag, simple_repo,  default_detectors):
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[-1])

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL]
    )

    assert next_tag in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag_on_last_commit(
        existing_tag, next_tag, simple_repo,  default_detectors):
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[0])

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL,
         '--skip-tag-if-one-already-present'])

    assert next_tag not in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag_append_v(
        existing_tag, next_tag, simple_repo,  default_detectors):
    """Test a simple flow locally."""

    repo = git.Repo(simple_repo, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[-1])

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL,
         '--append-v-to-tag']
    )

    assert 'v{}'.format(next_tag) in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_MINOR)
def test_simple_flow_existing_tag_minor_bump(
        existing_tag, next_tag, simple_repo_minor_commit):
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo_minor_commit, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[-1])

    entrypoint.main(
        ['-r', simple_repo_minor_commit,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL]
    )

    assert next_tag in repo.tags


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_MAJOR)
def test_simple_flow_existing_tag_major_bump(
        existing_tag, next_tag, simple_repo_major_commit):
    """Test a simple flow locally."""
    repo = git.Repo(simple_repo_major_commit, odbt=git.GitDB)
    repo.create_tag(
        existing_tag,
        ref=list(repo.iter_commits())[-1])

    entrypoint.main(
        ['-r', simple_repo_major_commit,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL]
    )

    assert next_tag in repo.tags


def test_push_to_remote(simple_repo, tmpdir):
    """Test the ability to push to remotes."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    cloned_repo_path = os.path.join(tmpdir, 'cloned-repo')

    cloned_repo = repo.clone(cloned_repo_path)

    entrypoint.main(
        ['-r', cloned_repo_path,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL,
         '-u', 'origin']
    )

    assert '0.0.1' in repo.tags
    assert '0.0.1' in cloned_repo.tags


def test_push_to_multiple_remotes(simple_repo, tmpdir, default_detectors):
    """Test the ability to push to remotes."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)
    cloned_repo_path = os.path.join(tmpdir, 'cloned-repo')
    second_remote_path = os.path.join(tmpdir, 'second_remote')

    cloned_repo = repo.clone(cloned_repo_path)
    second_remote = git.Repo.init(second_remote_path, odbt=git.GitDB)

    cloned_repo.create_remote('second_remote', second_remote.common_dir)

    entrypoint.main(
        ['-r', cloned_repo_path,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL,
         '-u', 'origin', 'second_remote'])

    assert '0.0.1' in cloned_repo.tags
    assert '0.0.1' in repo.tags
    assert '0.0.1' in second_remote.tags


def test_multiple_commits(simple_repo):
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

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL])

    assert '2.0.0' in repo.tags


def test_tag_message_has_heading(simple_repo):
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

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL])

    assert '2.0.0' in repo.tags
    for message in messages:
        assert message.split('\n')[0].strip() in repo.tags['2.0.0'].tag.message


def test_tag_message_user_exists_and_not_specified(simple_repo):
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    with repo.config_writer() as config_writer:
        config_writer.set_value('user', 'name', TEST_NAME)
        config_writer.set_value('user', 'email', TEST_EMAIL)

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL])

    assert '0.0.1' in repo.tags
    assert TEST_NAME == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL == repo.tags['0.0.1'].tag.tagger.email


def test_tag_message_user_exists_and_specified(simple_repo):
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    with repo.config_writer() as config_writer:
        config_writer.set_value('user', 'name', TEST_NAME)
        config_writer.set_value('user', 'email', TEST_EMAIL)

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME_2,
         '--email', TEST_EMAIL_2])

    assert '0.0.1' in repo.tags
    assert TEST_NAME_2 == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL_2 == repo.tags['0.0.1'].tag.tagger.email


def test_tag_message_user_exists_and_only_email_specified(simple_repo, default_detectors):
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    with repo.config_writer() as config_writer:
        config_writer.set_value('user', 'name', TEST_NAME)
        config_writer.set_value('user', 'email', TEST_EMAIL)

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--email', TEST_EMAIL_2])

    assert '0.0.1' in repo.tags
    assert TEST_NAME == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL_2 == repo.tags['0.0.1'].tag.tagger.email


def test_tag_message_user_does_not_exists_and_specified(simple_repo, default_detectors):
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME_2,
         '--email', TEST_EMAIL_2])
    assert '0.0.1' in repo.tags
    assert TEST_NAME_2 == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL_2 == repo.tags['0.0.1'].tag.tagger.email


def test_tag_message_user_exists_and_specify_make_sure_clean_env(simple_repo, default_detectors):
    """Test to see if the tag message has all the commit headings."""
    repo = git.Repo(simple_repo, odbt=git.GitDB)

    with repo.config_writer() as config_writer:
        config_writer.set_value('user', 'name', TEST_NAME)
        config_writer.set_value('user', 'email', TEST_EMAIL)

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--email', TEST_EMAIL_2])

    assert '0.0.1' in repo.tags
    assert TEST_NAME == repo.tags['0.0.1'].tag.tagger.name
    assert TEST_EMAIL_2 == repo.tags['0.0.1'].tag.tagger.email

    with repo.config_writer() as config_writer:
        repo_config_name = config_writer.get_value('user', 'name')
        repo_config_email = config_writer.get_value('user', 'email')

    assert TEST_NAME == repo_config_name
    assert TEST_EMAIL == repo_config_email


@pytest.mark.parametrize('existing_tag, next_tag',
                         TEST_DATA_SIMPLE_TAG_PATCH_BUMP)
def test_simple_flow_existing_tag_and_extra_tag_on_separate_branch(
        existing_tag, next_tag, simple_repo):
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

    entrypoint.main(
        ['-r', simple_repo,
         '-b', 'master',
         '--name', TEST_NAME,
         '--email', TEST_EMAIL])

    assert next_tag in repo.tags
