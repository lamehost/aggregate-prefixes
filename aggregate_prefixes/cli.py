#!/usr/bin/python

from __future__ import absolute_import
import fileinput
import sys
from itertools import ifilter

from aggregate_prefixes.aggregate_prefixes import aggregate_prefixes



def main():
    prefixes = ifilter(None, set([_.strip() for _ in fileinput.input()]))
    try:
        aggregates = aggregate_prefixes(prefixes)
    except (ValueError, TypeError), error:
        sys.exit(error)
    print '\n'.join(aggregates)


if __name__ == '__main__':
    main()
