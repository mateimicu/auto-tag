#!/usr/bin/env python3
"""
Automatically tags branches base on commit message
"""
import logging
from typing import (
    Callable,
    Tuple,
    Optional,
    List,
)

import semantic_version
import git

from auto_tag import constants
from auto_tag import detectors as auto_tag_detectors
from auto_tag import git_custom_env
from auto_tag import tag_search_strategy


class AutoTag():
    """Class  wrapper for auto-tag functionality."""

    def __init__(
            self, repo: str, branch: str,
            upstream_remotes: Optional[List[str]],
            detectors: List[auto_tag_detectors.BaseDetector],
            search_strategy: Callable = tag_search_strategy.DEFAULT_STRATEGY,  # type: ignore
            git_name: Optional[str] = None,
            git_email: Optional[str] = None,
            logger: Optional[logging.Logger] = None,
            append_v: bool = False, skip_if_exists: bool = False) -> None:
        """Initializa the AutoTag class.

        :param logger: If an existing logger is to be used
        :param args: CLI arguments
        """
        self._logger = logger or logging.getLogger(__name__)
        self._repo = repo
        self._detectors = detectors
        self._branch = branch
        self._upstream_remotes = upstream_remotes or []
        self._search_strategy = search_strategy
        self._git_name = git_name
        self._git_email = git_email
        self._append_v = append_v

        self._skip_if_exists = skip_if_exists

    def get_latest_tag(self, repo: git.Repo) -> Tuple[Optional[
            git.refs.tag.TagReference], Optional[semantic_version.Version]]:
        """Return the last tag for the given repo in a Version class.

        :param repo: git.Repository to query for tags
        :type repo: git.Repo

        :returns: The latest tag from the repository
        :rtype: (git.Tag, semantic_version.Version)
        """
        raw_tag = self._search_strategy(
            repo=repo, branch=self._branch)
        if raw_tag is None:
            return None, None
        sem_tag = semantic_version.Version(
            tag_search_strategy.clean_tag_name(str(raw_tag)))
        return raw_tag, sem_tag

    @staticmethod
    def bump_tag(
            tag: Optional[semantic_version.Version],
            change_type: int) -> semantic_version.Version:
        """Return the next tag version based on the change type."""
        if tag is None:
            return semantic_version.Version('0.0.1')

        if change_type == constants.MAJOR:
            return tag.next_major()

        if change_type == constants.MINOR:
            return tag.next_minor()

        return tag.next_patch()

    def get_all_commits_from_a_tag(
            self, repo: git.Repo, branch: str,
            tag: Optional[git.refs.tag.TagReference]) -> List[
                git.objects.commit.Commit]:
        """
        Return all commits from the branch that
        happened father the specified tag.

        :param repo: git.Repository to query for commits
        :type repo: git.Repo

        :param branch: Branch to work on
        :type branch: str

        :param repo: Tag to stop the query at.
        :type repo: semantic_version.Version

        :returns: List of commits.
        :rtype: list of git.objects.commit.Commit
        """
        stop_commit = None
        if str(tag) in repo.tags:
            stop_commit = repo.tags[str(tag)].commit

        commits = []
        for commit in repo.iter_commits(rev=branch):
            if commit == stop_commit:
                break
            commits.append(commit)
        self._logger.debug(
            'Commits found from after tag %s: %s', tag, commits)
        return commits

    def get_change_type(self, commits: List[git.objects.commit.Commit]) -> int:
        """Evaluate all detectors on a commit and decide on the change type."""
        change_type = constants.PATCH
        for commit in commits:
            for detector in self._detectors:
                if detector.evaluate(commit):
                    change_type = max(change_type, detector.change_type)

        return change_type

    @staticmethod
    def get_remote(repo: git.Repo, name: str) -> git.remote.Remote:
        """Return the git.remote.Remote object base on the name."""
        for remote in repo.remotes:
            if remote.name == name:
                return remote
        return None

    def push_to_remotes(self, repo: git.Repo, tag: str) -> None:
        """Push a tag to the specified remotes."""
        if self._upstream_remotes:
            self._logger.info('Start pushing to remotes: %s.',
                              self._upstream_remotes)
        else:
            self._logger.info('No push remote was specified')
            return
        for remote_name in self._upstream_remotes:
            remote = self.get_remote(repo, remote_name)
            if remote:
                self._logger.info('Push %s to %s', tag, remote)
                remote.push(str(tag))
            else:
                self._logger.error(
                    'Can\'t find remote with name `%s`', remote_name)

    @staticmethod
    def _create_tag_message(commits: List[git.objects.commit.Commit],
                            tag: semantic_version.Version) -> str:
        """Create a tag message that contains informations
        from the commits. """

        tag_message = 'Release {} \n\n'.format(str(tag))

        for message in [c.message for c in commits]:
            tag_message += '    * {}\n'.format(message.split('\n')[0].strip())
        return tag_message

    @staticmethod
    def _is_last_commit_already_tagged(
            repo: git.Repo,
            last_tag: Optional[git.refs.tag.TagReference],
            branch_name: str) -> bool:
        """Check if the last_tag is also applied on the latest commit."""
        if last_tag is None:
            return False
        commit = list(repo.iter_commits(rev=branch_name))[0]
        return last_tag.commit == commit

    def work(self) -> None:
        """Main entry point.

        :param args: Argument to work on
        """
        repo = git.Repo(self._repo, odbt=git.GitDB)
        self._logger.info('Start tagging %s', repo)
        last_tag, latest_tag_sem = self.get_latest_tag(repo)

        self._logger.info('Found tag %s', last_tag)
        commits = self.get_all_commits_from_a_tag(
            repo, self._branch, last_tag)
        type_of_change = self.get_change_type(commits)
        next_tag = self.bump_tag(latest_tag_sem, type_of_change)
        # NOTE(mmicu): Here we need to check if the next tag exists
        tag = 'v{}'.format(next_tag) if self._append_v else str(next_tag)

        self._logger.info('Bumping tag %s -> %s', last_tag, next_tag)

        with git_custom_env.GitCustomeEnvironment(repo.working_dir,
                                                  self._git_name,
                                                  self._git_email):
            tag_on_last_commit = self._is_last_commit_already_tagged(
                repo, last_tag, self._branch)

            if self._skip_if_exists and tag_on_last_commit:
                self._logger.info(
                    ('The tag is already tagged, following your CLI option'
                     ' we will skip tagging.'))
            else:
                repo.create_tag(
                    str(tag),
                    message=self._create_tag_message(commits, next_tag))

        self.push_to_remotes(repo, tag)
