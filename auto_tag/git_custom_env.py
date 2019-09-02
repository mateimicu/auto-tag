#!/usr/bin/env python3
"""
Automatically tags branches base on commit message
"""
import git


class GitCustomeEnvironment():
    """Custom Git Configuration context manager."""

    # pylint: disable=no-member
    def __init__(self, repo_path, name, email):
        """Initialize the context manager."""
        self._repo = git.Repo(repo_path, odbt=git.GitDB)
        self._name = name
        self._email = email
        self._old_name = None
        self._old_email = None
        with self._repo.config_writer() as confi_w:
            if confi_w.has_option('user', 'name'):
                self._old_name = confi_w.get_value('user', 'name')

            if confi_w.has_option('user', 'email'):
                self._old_email = confi_w.get_value('user', 'email')

    def __enter__(self):
        with self._repo.config_writer() as config_writer:
            if self._name is not None:
                config_writer.set_value('user', 'name', self._name)
            if self._email is not None:
                config_writer.set_value('user', 'email', self._email)

    def __exit__(self, _type, value, traceback):
        with self._repo.config_writer() as conf_w:
            if not conf_w.has_section('user'):
                return
            if self._old_name is None:
                conf_w.remove_option('user', 'name')
            else:
                conf_w.set_value('user', 'name', self._old_name)

            if self._old_email is None:
                conf_w.remove_option('user', 'email')
            else:
                conf_w.set_value('user', 'email', self._old_email)
