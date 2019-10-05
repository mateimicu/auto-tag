#!/usr/bin/env python3
"""
Package entry point.
"""
import sys
import logging
import logging.config

from auto_tag import core, cli, detectors_config, tag_search_strategy


def main(cli_args):
    """Main entry point for Auto-Tag module."""

    parser = cli.get_parser()
    args = parser.parse_args(cli_args)

    logger = logging.getLogger(__name__)
    # pylint:disable=no-member, protected-access
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

    if args.config:
        config = detectors_config.DetectorsConfig.from_file(
            args.config)
    else:
        config = detectors_config.DetectorsConfig.from_default()

    search_strategy = tag_search_strategy.SEARCH_METHODS_MAPPING[
        args.tag_search_strategy]
    autotag = core.AutoTag(
        repo=args.repo, branch=args.branch,
        upstream_remotes=args.upstream_remote,
        detectors=config.detectors,
        search_strategy=search_strategy,
        git_name=args.name, git_email=args.email,
        append_v=args.append_v_to_tag,
        skip_if_exists=args.skip_tag_if_one_already_present,
        logger=logger
    )
    autotag.work()


if __name__ == '__main__':
    main(sys.argv[1:])
