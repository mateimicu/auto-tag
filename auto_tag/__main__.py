#!/usr/bin/env python3
"""
Package entry point.
"""
import sys

from auto_tag import core, cli


def main():
    parser = cli.get_parser()
    args = parser.parse_args(sys.argv[1:])
    core.work(args)


if __name__ == '__main__':
    main()
