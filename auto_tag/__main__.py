#!/usr/bin/env python3
"""
Package entry point.
"""
import sys

from auto_tag import entrypoint

def main():
    """Main entry point for module and cli."""
    entrypoint.main(sys.argv[1:])


if __name__ == '__main__':
    main()
