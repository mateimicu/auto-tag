#!/usr/bin/env python3
"""
Test simple flows of the AutoTag application
"""
import os

import git
import pytest
import time

from auto_tag import tag_search_strategy
# pylint:disable=invalid-name


SCENARIOS = [
    (tag_search_strategy.get_biggest_tag_in_repo, 'branch_a', '1.1.1'),
    (tag_search_strategy.get_biggest_tag_in_branch, 'branch_a', '1.0.1'),
    (tag_search_strategy.get_latest_tag_in_repo, 'branch_a', '1.1.1'),
    (tag_search_strategy.get_latest_tag_in_branch, 'branch_a', '0.1.1'),
]


@pytest.mark.parametrize('search_strategy, target_branch, expected_tag',
                         SCENARIOS)
def test_tag_search_strategy(search_strategy, target_branch, expected_tag,
                             simple_repo_two_branches):
    """Test to see if `get_biggest_tag_in_repo` returns the biggest tag
       from all branches

    Idea:
        If we have two branches `banch_a` and `branch_b`
        `branch_a` has the following tags applied in this order: 
            `0.0.1`
            `1.0.1`
            `0.1.1`
        `branch_b` has the following tags applied in this order: 
            `1.1.1`
    """
    repo = git.Repo(simple_repo_two_branches, odbt=git.GitDB)

    # search for tag
    found_tag = search_strategy(repo=repo, branch=target_branch)
    assert found_tag is not None
    assert found_tag.name == expected_tag
