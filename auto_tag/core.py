#!/usr/bin/env python3
"""
Automatically tags branches base on commit message
"""
import semantic_version
from git import Repo


# Types of changes
MAJOR = 100
MINOR = 10
PATCH = 1

PREFIX_TO_ELIMINATE = ['v']


def _clean_tag_name(tag_name):
    """Remove common mistakes when using semantic versioning."""
    for prefix in PREFIX_TO_ELIMINATE:
        if tag_name.startswith(prefix):
            return tag_name[len(prefix):]
    return tag_name


def get_latest_tag(repo):
    """Return the last tag for the given repo in a Version class.
    :param repo: Repository to query for tags
    :type repo: git.Repo

    :returns: The latest tag from the repository. If there are not tags it
              will return `0.0.1`
    :rtype: semantic_version.Version
    """
    tags_name = [_clean_tag_name(tag.name) for tag in repo.tags]
    sem_versions = [
        semantic_version.Version(tag_name) for tag_name in tags_name
    ]
    if sem_versions:
        return max(sem_versions)
    return semantic_version.Version('0.0.1')


def bump_tag(tag, change_type):
    """Return the next tag version based on the change type."""
    if change_type == MAJOR:
        return tag.next_major()
    elif change_type == MINOR:
        return tag.next_minor()
    return tag.next_patch()


def get_all_commits_from_a_tag(repo, branch, tag):
    """
    Return all commits from the branch that happened father the specified tag.

    :param repo: Repository to query for commits
    :type repo: git.Repo

    :param branch: Branch to work on
    :type branch: str

    :param repo: Tag to stop the query at.
    :type repo: semantic_version.Version

    :returns: List of commits.
    :rtype: list of git.Commit
    """
    stop_commit = None
    if str(tag) in repo.tags:
        stop_commit = repo.tags[str(tag)].commit

    commits = []
    for commit in repo.iter_commits(rev=branch):
        if commit == stop_commit:
            break
        commits.append(commit)
    return commits


def get_change_type(commits):
    """Based on the commit message decide the change type.
    Change types can be PATCH, MINOR, MAJOR.

    Everything by default is a PATCH

    If the message stars with `fix` -> it remains a PATCH
    If the message starts with `feat` -> it becomes a MINOR

    If the message contains `BREAKING_CHANGE` -> it becomes a MAJOR

        :Example:

        ```
        fix(msk): fix logging bug
        ```
        This is a PATCH

        ```
        feature(rds): add multi AZ support
        ```
        This is a MINOR

        ```
        fix(msk): fix logging bug
        BREAKING_CHANGE: Introduce mandatory configuration
        ```
        This is a MAJOR

        ```
        feature(rds): add multi AZ support

        BREAKING_CHANGE: Requires downtime
        ```
        This is a MAJOR

    :param commits: List of commits
    :type: list of git.Commit

    :return: Type of change (PATCH, MINOR, MAJOR). By default everything
             is a PATCH
    :rtype: int (constants)
    """
    change_type = PATCH
    for commit in commits:
        if commit.message.strip().startswith('feature('):
            change_type = max(change_type, MINOR)

        if 'BREAKING_CHANGE' in commit.message.upper():
            change_type = MAJOR

    return change_type


def get_remote(repo, name):
    """Return the git.Remote object base on the name."""
    for remote in repo.remotes:
        if remote.name == name:
            return remote


def work(args):
    """Main entry point.

    :param args: Argument to work on
    """
    repo = Repo(args.repo)
    last_tag = get_latest_tag(repo)
    commits = get_all_commits_from_a_tag(repo, args.branch, last_tag)
    type_of_change = get_change_type(commits)
    next_tag = bump_tag(last_tag, type_of_change)
    repo.create_tag(str(next_tag))

    for remote_name in args.upstream_remote:
        remote = get_remote(repo, remote_name)
        if remote:
            remote.push(str(next_tag))
