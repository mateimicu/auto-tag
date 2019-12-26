#!/usr/bin/env python3
"""
Automatically tags branches base on commit message
"""
import time
from typing import Any
from typing import List
from typing import Optional

import git
import semantic_version

from auto_tag import constants
from auto_tag import exception


# pylint: disable=unused-argument
def clean_tag_name(tag_name: str) -> str:
    """Remove common mistakes when using semantic versioning."""
    for prefix in constants.PREFIX_TO_ELIMINATE:
        if tag_name.startswith(prefix):
            clean_tag = tag_name[len(prefix):]
            return clean_tag
    return tag_name


def get_biggest_tag_in_repo(
        repo: git.Repo, *args: Any, **kwargs: Any) -> git.refs.tag.TagReference:
    """Return the last tag for the given repo in a Version class.
    :param repo: Repository to query for tags
    :type repo: git.Repo

    :returns: The latest tag from the repository.
    :rtype: str
    """
    sem_versions = [
        (
            tag,
            semantic_version.Version(clean_tag_name(tag.name))
        ) for tag in repo.tags
    ]

    if sem_versions:
        latest_tag, _ = max(sem_versions, key=lambda x: x[1])
        return latest_tag
    return None


def _get_tags_on_branch(
        repo: git.Repo,
        branch_name: str) -> List[git.refs.tag.TagReference]:
    """Get all the tags on this specific branch.

    :param repo: Repository to query for tags
    :type repo: git.Repo

    :param branch_name: name of the branch
    :type branch_name: string

    :returns: List of tags from this branch
    :rtype: list
    """
    commits_to_tag = {tag.commit: tag for tag in repo.tags}
    found_tags = []

    for commit in repo.iter_commits(rev=branch_name):
        if commit in commits_to_tag:
            found_tags.append(
                commits_to_tag[commit])
    return found_tags


def get_biggest_tag_in_branch(
        repo: git.Repo, branch: str, *args: Any,
        **kwargs: Any) -> Optional[git.refs.tag.TagReference]:
    """Return the last tag for the given repo in a Version class.
    :param repo: Repository to query for tags
    :type repo: git.Repo

    :returns: The latest tag from the repository
    :rtype: str
    """
    tags = _get_tags_on_branch(repo, branch)

    sem_versions = [
        (
            tag,
            semantic_version.Version(clean_tag_name(tag.name))
        ) for tag in tags
    ]
    if sem_versions:
        latest_tag, _ = max(sem_versions, key=lambda x: x[1])
        return latest_tag
    return None


def get_latest_tag_in_repo(
        repo: git.Repo, branch: str, *args: Any,
        **kwargs: Any) -> git.refs.tag.TagReference:
    """Return the last tag for the given repo in a Version class.
    :param repo: Repository to query for tags
    :type repo: git.Repo

    :returns: The latest tag from the repository
    :rtype: str
    """
    committed_date_to_tag = [
        (time.gmtime(tag.commit.committed_date), tag) for tag in repo.tags
    ]
    # if there are no tags
    if not committed_date_to_tag:
        return None

    committed_date_to_tag.sort(key=lambda x: x[0], reverse=True)

    return committed_date_to_tag[0][1]


def get_latest_tag_in_branch(
        repo: git.Repo, branch: str, *args: Any,
        **kwargs: Any) -> git.refs.tag.TagReference:
    """Return the last tag for the given repo in a Version class.
    :param repo: Repository to query for tags
    :type repo: git.Repo

    :returns: The latest tag from the repository
    :rtype: str
    """
    committed_date_to_tag = [
        (
            time.gmtime(tag.commit.committed_date),
            tag
        ) for tag in _get_tags_on_branch(repo, branch)
    ]
    # if there are no tags
    if not committed_date_to_tag:
        return None

    committed_date_to_tag.sort(key=lambda x: x[0], reverse=True)

    return committed_date_to_tag[0][1]


SEARCH_METHODS_MAPPING = {
    constants.SEARCH_STRATEGY_BIGGEST_TAG_IN_REPO:
        get_biggest_tag_in_repo,

    constants.SEARCH_STRATEGY_BIGGEST_TAG_IN_BRANCH:
        get_biggest_tag_in_branch,

    constants.SEARCH_STRATEGY_LATEST_TAG_IN_REPO:
        get_latest_tag_in_repo,

    constants.SEARCH_STRATEGY_LATEST_TAG_IN_BRANCH:
        get_latest_tag_in_branch
}

DEFAULT_STRAGETY_NAME = constants.SEARCH_STRATEGY_BIGGEST_TAG_IN_BRANCH
DEFAULT_STRATEGY = SEARCH_METHODS_MAPPING[DEFAULT_STRAGETY_NAME]


def get_last_tag(repo: git.Repo, branch: str,
                 search_method_name: str) -> git.refs.tag.TagReference:
    """Get the last tag according to the appropriate search strategy."""
    search_strategy: Any = SEARCH_METHODS_MAPPING.get(
        search_method_name, None)

    if search_strategy is None:
        raise exception.UnknowkSearchStrategy(
            '{} is not a search strategy supported.Choose form {}'.format(
                search_method_name, SEARCH_METHODS_MAPPING.keys()))

    return search_strategy(repo=repo, branch=branch)
