# -*- coding: utf-8 -*-

"""
Provides CLI interface for package aggregate-prefixes
"""

from __future__ import absolute_import
from __future__ import print_function
import argparse
import sys

from aggregate_prefixes.aggregate_prefixes import aggregate_prefixes
from aggregate_prefixes import __version__ as VERSION

def main():
    """
    Aggregates IPv4 or IPv6 prefixes from file or STDIN.

    Reads a list of unsorted IPv4 or IPv6 prefixes from a file or STDIN.
    Returns a sorted list of aggregates to STDOUT.
    """

    parser = argparse.ArgumentParser(
        prog='aggregate-prefixes',
        description='Aggregates IPv4 or IPv6 prefixes from file or STDIN'
    )
    parser.add_argument(
        'prefixes',
        type=argparse.FileType('r'),
        default=sys.stdin
    )
    parser.add_argument(
        '--max-length', '-m',
        metavar='LENGTH',
        type=int,
        help='Discard longer prefixes prior to processing',
        default=128
    )
    parser.add_argument(
        '--verbose', '-v',
        help='Display verbose information about the optimisations',
        action='store_true'
    )
    parser.add_argument(
        '--version', '-V',
        action='version',
        version='%(prog)s ' + VERSION
    )
    args = parser.parse_args()

    # Read and cleanup prefixes
    prefixes = [_ for _ in set([_.strip() for _ in args.prefixes]) if _]
    try:
        aggregates = aggregate_prefixes(prefixes, args.max_length, args.verbose)
    except (ValueError, TypeError) as error:
        sys.exit(error)
    print('\n'.join(aggregates))


if __name__ == '__main__':
    main()
