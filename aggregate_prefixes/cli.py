# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2018, Marco Marzetti <marco@lamehost.it>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


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
        help='Unsorted list of IPv4 or IPv6 prefixes. Use \'-\' for STDIN.',
        default=sys.stdin
    )
    parser.add_argument(
        '--max-length', '-m',
        nargs='?',
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
    prefixes = [
        p for p in set([
            # Read lines in split those after whitespaces, skip comments and return the rest
            p.strip() for line in args.prefixes for p in line.split(' ') if not p.startswith('#')
        ])
        # Skip empty strings
        if p
    ]
    try:
        aggregates = aggregate_prefixes(prefixes, args.max_length, args.verbose)
    except (ValueError, TypeError) as error:
        sys.exit('ERROR: %s' % error)
    print('\n'.join(aggregates))


if __name__ == '__main__':
    main()
