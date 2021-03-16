# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2019, Marco Marzetti <marco@lamehost.it>

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
from __future__ import unicode_literals
import argparse
import sys

from aggregate_prefixes import aggregate_prefixes
from .__about__ import __version__ as VERSION

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
        nargs='?',
        help='Text file of unsorted list of IPv4 or IPv6 prefixes. Use \'-\' for STDIN.',
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
        '--truncate', '-t',
        metavar='MASK',
        type=int,
        help='Truncate IP/mask to network/mask',
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
    prefixes = {
            prefix
            # Walk through lines
            for line in args.prefixes
            if (
                # Skip comments and strip lines
                prefixes:= next(iter(
                    line.split('#')
                )).strip()
            )
            # Skip empty lines
            and prefixes
            # Multiple prefixes per line separated by space are supported
            for prefix in prefixes.split(' ')
    }

    try:
        # Aggregate
        aggregates = aggregate_prefixes(prefixes, args.max_length, args.truncate, args.verbose)
    except (ValueError, TypeError) as error:
        sys.exit('ERROR: %s' % error)

    # Print aggregates one per line
    print(
        '\n'.join(map(str, aggregates))
    )


if __name__ == '__main__':
    main()
