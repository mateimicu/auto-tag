# Auto-Tag
[![Updates](https://pyup.io/repos/github/mateimicu/auto-tag/shield.svg)](https://pyup.io/repos/github/mateimicu/auto-tag/)
[![Python 3](https://pyup.io/repos/github/mateimicu/auto-tag/python-3-shield.svg)](https://pyup.io/repos/github/mateimicu/auto-tag/)
![PyPI](https://img.shields.io/pypi/v/auto-tag)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/auto-tag)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/auto-tag)
[![codecov](https://codecov.io/gh/mateimicu/auto-tag/branch/master/graph/badge.svg)](https://codecov.io/gh/mateimicu/auto-tag)
![PyPI - License](https://img.shields.io/pypi/l/auto-tag)


Automatically tag a branch with the following SemVersion tag.

This is useful if you want to automatically tag something merged on the master, for example, microservices.
If there is a trigger based on tags then this can be used to apply the tags.


# TOC

 - [Install](#how-to-install)
 - [How it Works](#how-it-works)
 - [Exampels](#examples)
 - [Detectors](#detectors)
 - [Git Author](#git-author)

# How to install

```bash
~ $ pip install auto-tag
```

To see if it works, you can try

```bash
~ $ auto-tag  -h
usage: auto-tag [-h] [-b BRANCH] [-r REPO]
                [-u [UPSTREAM_REMOTE [UPSTREAM_REMOTE ...]]]
                [-l {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}]
                [--name NAME] [--email EMAIL] [-c CONFIG]
                [--skip-tag-if-one-already-present] [--append-v-to-tags]

Tag branch based on commit messages

optional arguments:
  -h, --help            show this help message and exit
  -b BRANCH, --branch BRANCH
                        On what branch to work on. Default `master`
  -r REPO, --repo REPO  Path to repository. Default `.`
  -u [UPSTREAM_REMOTE [UPSTREAM_REMOTE ...]], --upstream_remote [UPSTREAM_REMOTE [UPSTREAM_REMOTE ...]]
                        To what remote to push to.Can be specified multiple
                        time.
  -l {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}, --logging {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}
                        Logging level.
  --name NAME           User name used for creating git objects.If not
                        specified the system one will be used.
  --email EMAIL         Email name used for creating git objects.If not
                        specified the system one will be used.
  -c CONFIG, --config CONFIG
                        Path to detectors configuration.
  --skip-tag-if-one-already-present
                        If a tag is already present on the latest commit don't
                        apply a new tag
  --append-v-to-tags    Append a v to the tag (ex v1.0.5)
```

# How it Works

The flow is as follows:
- figure our repository based on the argument
- load detectors from file if specified (`-c` option), if none specified load default ones (see [Detectors](#detectors))
- check for the last tag 
- look at all commits done after that tag on a specific branch (or from the start of the repository if no tag is found)
- apply the detector (see [Detectors](#detectors)) on each commit and save the highest change detected (PATH, MINOR, MAJOR)
- bump the last tag with the approbate change  and apply it using the default git author in the system or a specific one (see [Git Author](#git-author))
- if an upstream was specified push the tag to that upstream


# Examples
Here we can see in commit `2245d5d` that it stats with `feature(`
so the latest know tag (`0.2.1`) was bumped to `0.3.0`
```
~ $ git log --oneline
2245d5d (HEAD -> master) feature(component) commit #4
939322f commit #3
9ef3be6 (tag: 0.2.1) commit #2
0ee81b0 commit #1
~ $ auto-tag
2019-08-31 14:10:24,626: Start tagging <git.Repo "/Users/matei/git/test-auto-tag-branch/.git">
2019-08-31 14:10:24,649: Bumping tag 0.2.1 -> 0.3.0
2019-08-31 14:10:24,658: No push remote was specified
~ $ git log --oneline
2245d5d (HEAD -> master, tag: 0.3.0) feature(component) commit #4
939322f commit #3
9ef3be6 (tag: 0.2.1) commit #2
0ee81b0 commit #1
```

In this example we can see `2245d5deb5d97d288b7926be62d051b7eed35c98` introducing a feature that will trigger a MINOR change but we can also see `0de444695e3208b74d0b3ed7fd20fd0be4b2992e` having a `BREAKING_CHANGE` that will introduce a MAJOR bump, this is the reason the tag moved from `0.2.1` to `1.0.0`
```
~ $ git log
commit 0de444695e3208b74d0b3ed7fd20fd0be4b2992e (HEAD -> master)
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 21:58:01 2019 +0300

    fix(something) ....

    BREAKING_CHANGE: this must trigger major version bump

commit 65bf4b17669ea52f84fd1dfa4e4feadbc299a80e
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 21:57:47 2019 +0300

    fix(something) ....

commit 2245d5deb5d97d288b7926be62d051b7eed35c98
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 19:52:10 2019 +0300

    feature(component) commit #4

commit 939322f1efaa1c07b7ed33f2923526f327975cfc
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 19:51:24 2019 +0300

    commit #3

commit 9ef3be64c803d7d8d3b80596485eac18e80cb89d (tag: 0.2.1)
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 19:51:18 2019 +0300

    commit #2

commit 0ee81b0bed209941720ee602f76341bcb115b87d
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 19:50:25 2019 +0300

    commit #1
~ $ auto-tag
2019-08-31 14:10:24,626: Start tagging <git.Repo "/Users/matei/git/test-auto-tag-branch/.git">
2019-08-31 14:10:24,649: Bumping tag 0.2.1 -> 1.0.0
2019-08-31 14:10:24,658: No push remote was specified
~ $ git log
commit 0de444695e3208b74d0b3ed7fd20fd0be4b2992e (HEAD -> master, tag: 1.0.0)
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 21:58:01 2019 +0300

    fix(something) ....

    BREAKING_CHANGE: this must trigger major version bump

commit 65bf4b17669ea52f84fd1dfa4e4feadbc299a80e
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 21:57:47 2019 +0300

    fix(something) ....

commit 2245d5deb5d97d288b7926be62d051b7eed35c98
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 19:52:10 2019 +0300

    feature(component) commit #4

commit 939322f1efaa1c07b7ed33f2923526f327975cfc
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 19:51:24 2019 +0300

    commit #3

commit 9ef3be64c803d7d8d3b80596485eac18e80cb89d (tag: 0.2.1)
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 19:51:18 2019 +0300

    commit #2

commit 0ee81b0bed209941720ee602f76341bcb115b87d
Author: Matei-Marius Micu <micumatei@gmail.com>
Date:   Fri Aug 30 19:50:25 2019 +0300

    commit #1
```
# Detectors

If you want to detect what commit enforces a specific tag bump(PATH, MINOR, MAJOR) you can configure detectors.
They are configured in a yaml file that looks like this:
```yaml
detectors:

  check_for_feature_heading:
    type: CommitMessageHeadStartsWithDetector
    produce_type_change: MINOR
    params:
      pattern: 'feature'


  check_for_breaking_change:
    type: CommitMessageContainsDetector
    produce_type_change: MAJOR
    params:
      pattern: 'BREAKING_CHANGE'
      case_sensitive: false
```
Here is the default configuration for detectors if none is specified.
We can see we have two detectors `check_for_feature_heading` and `check_for_breaking_change`, with a type, what change they will trigger and specific parameters for each one.
This configuration will do the following:
- if the commit message  starts with `feature(` a MINOR change will BE triggered
- if the commit has `BREAKIN_CHANGE` in the message a MAJOR change will be triggered
The bump on the tag will be based on the higher priority found.

The `type` and `produce_type_change` parameters are required `params` is specific to every detector.

To pass the file to the process just use the `-c` CLI parameter.

Currently we support the following triggers:
  - CommitMessageHeadStartsWithDetector
    - Parameters:
      - `case_sensitive` of type `bool`, if the comparison is case sensitive
      - `strip` of type `bool`, if we strip the spaces from the commit message
      - `pattern` of type `string`, what pattern is searched at the start of the commit message
  - CommitMessageContainsDetector
      - `case_sensitive` of type `bool`, if the comparison is case sensitive
      - `strip` of type `bool`, if we strip the spaces from the commit message
      - `pattern` of type `string`, what pattern is searched in the body of the commit message
  - CommitMessageMatchesRegexDetector
      - `strip` of type `bool`, if we strip the spaces from the commit message
      - `pattern` of type `string`, what regex pattern to match against the commit message

The regex detector is the most powerful one.

# Git Author
When creating and tag we need to specify a git author, if a global one is not set (or if we want to make this one with a specific user), we have the option to specify one.
The following options will add a temporary config to this repository(local config). After the tag was created it will restore the existing config (if any was present)
```
  --name NAME           User name used for creating git objects.If not
                        specified the system one will be used.
  --email EMAIL         Email name used for creating git objects.If not
                        specified the system one will be used.
```
If another user interacts with git while this process is taking place it will use the temporary config, but we assume we are run in a CI pipeline and this is the only process interacting with git.

---
This project is licensed under the terms of the MIT license.

