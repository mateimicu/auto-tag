#!/usr/bin/env python3
"""
Package entry point.
"""
import sys
import logging
import logging.config

from auto_tag import core, cli


def main():
    """Main entry point for Auto-Tag module."""

    parser = cli.get_parser()
    args = parser.parse_args(sys.argv[1:])

    logger = logging.getLogger(__name__)
    logger.setLevel(logging._nameToLevel[args.logging])
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s: %(message)s')

    # add formatter to console_handler
    console_handler.setFormatter(formatter)

    # add console_handler to logger
    logger.addHandler(console_handler)

    autotag = core.AutoTag(
        repo=args.repo, branch=args.branch,
        upstream_remotes=args.upstream_remote,
        logger=logger
    )
    autotag.work()


if __name__ == '__main__':
    main()
