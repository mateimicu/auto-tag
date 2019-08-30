# Auto-Tag
Automatically tag a branch with the following SemVersion tag.

The flow is as follows:
- check for the last tag 
- look at all commits done father that tag on a specific branch
- inspect the commit message for special markers to see how to bump the tag
	* by default everything is PATH change
	* if it starts with `feature(` -> MINOR
	* if it has `BREAKIN_CHANGE` in the message -> MAJOR
- bump the last tag with the approbate change 

```bash
~ $ auto-tag  -h
usage: auto-tag [-h] [-b BRANCH] [-r REPO] [-u UPSTREAM_REMOTE]

Tag branch based on commit messages

optional arguments:
  -h, --help            show this help message and exit
  -b BRANCH, --branch BRANCH
                        On what branch to work on. Default `master`
  -r REPO, --repo REPO  Path to repository. Default `.`
  -u UPSTREAM_REMOTE, --upstream_remote UPSTREAM_REMOTE
                        To what remote to push to. Default `origin`
```

## Examples
Here we can see in commit `2245d5d` that it stats with `feature(`
so the latest know tag (`0.2.1`) was bumped to `0.3.0`
```
~ $ git log --oneline
2245d5d (HEAD -> master) feature(component) commit #4
939322f commit #3
9ef3be6 (tag: 0.2.1) commit #2
0ee81b0 commit #1
~ $ auto-tag
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
(.venv) matei @ RO-IAS-LPT-C02VW35WG8WN ~/git/test-auto-tag-branch (master)
~ $ auto-tag
(.venv) matei @ RO-IAS-LPT-C02VW35WG8WN ~/git/test-auto-tag-branch (master)
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

Todo
- add logging
- add documentation
- add sanity tests
- add licensing and how to contribute informations
- add a pipeline for tests/linting (and maybe publishing)
- configure markers for MINOR and MAJOR
