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
Provides core functions for package aggregate-prefixes
"""

from __future__ import absolute_import
from __future__ import print_function

import sys

import ipaddr


def aggregate_prefixes(prefixes, max_length=128, debug=False):
    """
    Aggregates IPv4 or IPv6 prefixes.

    Gets a list of unsorted IPv4 or IPv6 prefixes and returns a sorted list of aggregates.

    Parameters
    ----------
    prefixes : list
        Unsorted list of IPv4 or IPv6 prefixes serialized as strings or ipaddr objects
    max_length: int
        Discard longer prefixes prior to processing
    debug: bool
        Write debug information on STDOUT

    Returns
    -------
    list
        Sorted list of IPv4 or IPv6 aggregated prefixes serialized as strings

    """
    aggregates = list()
    # Sort and filter prefixes. Smaller network goes firt, on tie larger prefixlen wins
    prefixes = sorted(
        [p for p in [ipaddr.IPNetwork(p) for p in prefixes] if p.prefixlen <= max_length],
        key=lambda p: (p.network, p.prefixlen)
    )
    if debug:
        print("PREFIXES: %s\n" % ', '.join([str(_) for _ in prefixes]), file=sys.stderr)

    _id = 0
    total_prefixes = len(prefixes)
    while _id < total_prefixes:
        prefix = prefixes[_id]
        if debug:
            print ("LOOP START -->\n", file=sys.stderr)
            print(
                "PREFIX: %s (Network: %s, Broadcast: %s)" % (
                    prefix, prefix.network, prefix.broadcast
                ), file=sys.stderr
            )
        # Assuming current is the only contigous prefix in the list
        contigous_prefixes = [prefix]
        last_contigous = prefix

        # Find list of contigous prefixes
        next_id = _id + 1
        while next_id < total_prefixes:
            last_contigous = contigous_prefixes[-1]
            next_prefix = prefixes[next_id]
            if debug:
                print(
                    "NEXT: %s (Network: %s, Broadcast: %s)" % (
                        next_prefix, next_prefix.network, next_prefix.broadcast
                    ), file=sys.stderr
                )
            # Current prefix is larger than next one
            if last_contigous.broadcast >= next_prefix.broadcast:
                next_id += 1
                continue
            # Next prefix is not contigous, loop ends here
            if last_contigous.broadcast+1 != next_prefix.network:
                break
            contigous_prefixes.append(next_prefix)
            next_id += 1
        last_contigous = contigous_prefixes[-1]

        # Move position forward to next non contigous prefix
        _id = next_id

        # Aggregate contigous prefixes
        contigous_id = 0
        total_contigous = len(contigous_prefixes)
        while contigous_id < total_contigous:
            first_contigous = contigous_prefixes[contigous_id]
            if debug:
                print(
                    "\nCONTIGOUS: %s" % ', '.join(
                        [str(_) for _ in contigous_prefixes[contigous_id:]]
                    ), file=sys.stderr
                )
                print(
                    "FIRST: %s (Network: %s, Broadcast: %s)" % (
                        first_contigous, first_contigous.network, first_contigous.broadcast
                    ), file=sys.stderr
                )
                print(
                    "LAST: %s (Network: %s, Broadcast: %s)" % (
                        last_contigous, last_contigous.network, last_contigous.broadcast
                    ), file=sys.stderr
                )
            # Assume new aggregate is this contigous
            aggregate = first_contigous
            tentative_len = first_contigous.prefixlen
            while tentative_len > 0:
                tentative_len -= 1
                # Calculate new tentative prefix
                tentative = ipaddr.IPNetwork('%s/%d' % (first_contigous.network, tentative_len))
                if debug:
                    print(
                        "TENTATIVE: %s (Network: %s, Broadcast: %s)" % (
                            tentative, tentative.network, tentative.broadcast
                        ), file=sys.stderr
                    )
                # Stop loop if bit boundaries are exceeded
                if tentative.network != first_contigous.network \
                    or tentative.broadcast > last_contigous.broadcast:
                    break
                aggregate = tentative
            # Found a new aggregate
            if debug:
                print(
                    "AGGREGATE: %s (Network: %s, Broadcast: %s)" % (
                        aggregate, aggregate.network, aggregate.broadcast
                    ), file=sys.stderr
                )
            # Find how many contigous the aggregate spans
            covered_id = contigous_id + 1
            while covered_id < total_contigous:
                if debug:
                    print(
                        "TESTING: %s (Network: %s, Broadcast: %s)" % (
                            contigous_prefixes[covered_id],
                            contigous_prefixes[covered_id].network,
                            contigous_prefixes[covered_id].broadcast
                        ), file=sys.stderr
                    )
                if aggregate.broadcast < contigous_prefixes[covered_id].network:
                    break
                covered_id += 1
            if debug:
                print(
                    "COVERED: %s\n" % ', '.join(
                        [str(_) for _ in contigous_prefixes[contigous_id:covered_id]]
                    ), file=sys.stderr
                )
            contigous_id = covered_id

            yield '%s/%d' % (aggregate.network, aggregate.prefixlen)

        if debug:
            print("<-- LOOP END", file=sys.stderr)
    if debug:
        print("", file=sys.stderr)
