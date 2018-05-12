# -*- coding: utf-8 -*-

"""
Provides CLI interface for package aggregate-prefixes
"""

from __future__ import absolute_import
from __future__ import print_function
import fileinput
import sys
try:
    # Python 2
    from future_builtins import filter
except ImportError:
    # Python 3
    pass

from aggregate_prefixes.aggregate_prefixes import aggregate_prefixes


def main():
    """
    Aggregates IPv4 or IPv6 prefixes from file or STDIN.

    Reads a list of unsorted IPv4 or IPv6 prefixes from a file or STDIN.
    Returns a sorted list of aggregates to STDOUT.
    """

    prefixes = filter(None, set([_.strip() for _ in fileinput.input()]))
    try:
        aggregates = aggregate_prefixes(prefixes)
    except (ValueError, TypeError) as error:
        sys.exit(error)
    print('\n'.join(aggregates))


if __name__ == '__main__':
    main()
