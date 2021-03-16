# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2021, Marco Marzetti <marco@lamehost.it>

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


import sys
import ipaddress


def find_aggregatables(prefixes):
    """
    Split prefix lists into aggregatable chunks

    Parameters:
    -----------
    prefixes : list
        Sorted list of IPv4 or IPv6 prefixes serialized as ipaddr objects

    Returns
    -------
    generator
        Iterable made of sorted list of aggregatable IPv4 or IPv6 prefixes serialized as ipaddress
    """
    # Add first item to a chunk
    try:
        prefix = next(iter(prefixes))
    except StopIteration:
        return
    aggregatable = [prefix]

    # broadcast means last prefix's broadcast
    broadcast = prefix.broadcast_address

    # Walk over prefixes
    for prefix in prefixes[1:]:
        # If network is smaller than broadcast, then prefix is subnetwork of current chunk member
        if prefix.network_address <= broadcast:
            continue
        # If network starts right after broadcast, then prefixes might be aggreagatable
        if broadcast + 1 == prefix.network_address:
            aggregatable.append(prefix)
        # Else, just save current and start a new chunk
        else:
            yield aggregatable
            aggregatable = [prefix]
        broadcast = prefix.broadcast_address
    yield aggregatable



def aggregate_aggregatable(aggregatable, debug=False):
    """
    Aggregates aggregatable chunks

    Parameters:
    -----------
    aggregatable : list
        Sorted list of aggregatable IPv4 or IPv6 prefixes serialized as ipaddress

    Returns
    -------
    generator
        Aggregates serialized as ipaddress
    """
    if debug:
        sys.stderr.write('Aggregatables: %s\n' % ', '.join(map(str, aggregatable)))
    aggregatable_end = aggregatable[-1].broadcast_address

    # Assume first item is an agggregte
    try:
        aggregate = next(iter(aggregatable))
    except StopIteration:
        return
    aggregate_end = False

    for prefix in aggregatable:
        # Skip prefixes that are part of the current aggregate
        if aggregate_end and aggregate_end >= prefix.broadcast_address:
            if debug:
                sys.stderr.write('  Skipping: %s\n' % prefix)
            continue
        if debug:
            sys.stderr.write(' Prefix: %s\n' % prefix)

        # Iteratively reduce aggregate length
        for tentative_len in range(prefix.prefixlen, -1, -1):
            tentative = ipaddress.ip_network(
                '%s/%d' % (prefix.network_address, tentative_len), False
            )
            if debug:
                sys.stderr.write('  Tentative aggregate: %s\n' % tentative)
            # If boundaries are exceeded, then exit the loop
            if prefix.network_address != tentative.network_address or \
                tentative.broadcast_address > aggregatable_end:
                if debug:
                    sys.stderr.write('  Boundaries exceeded by netmask: /%d\n' % tentative_len)
                break

            # At the end of every loop, consider the update aggregate to current length
            aggregate = tentative
            aggregate_end = aggregate.broadcast_address

        # Return aggregate
        if debug:
            sys.stderr.write(' Aggregate found: %s\n' % aggregate)
        yield aggregate


def aggregate_prefixes(prefixes, max_length=128, truncate=False, debug=False):
    """
    Aggregates IPv4 or IPv6 prefixes.

    Gets a list of unsorted IPv4 or IPv6 prefixes and returns a sorted iterable of aggregates.

    Parameters
    ----------
    prefixes : list
        Unsorted list of IPv4 or IPv6 prefixes serialized as strings or ipaddr objects
    max_length: int
        Discard longer prefixes prior to processing
    truncate:
        Truncate IP/mask to network/mask
    debug: bool
        Write debug information on STDOUT

    Returns
    -------
    generator
        Sorted iterable of IPv4 or IPv6 aggregated prefixes serialized as strings
    """

    # Translate prefixes into a parsable data structure and discard those that exceed maxlen
    prefixes = [
        prefix
        for text in prefixes
        if (prefix := ipaddress.ip_network(text, False)) and prefix.prefixlen <= max_length
    ]

    # Apply truncate
    if truncate:
        prefixes = [
            ipaddress.ip_network('%s/%d' % (prefix.network_address, truncate), False)
            if prefix.prefixlen > truncate
            else prefix
            for prefix in prefixes
        ]

    # Sort and filter prefixes. Smaller network goes firt, on tie larger prefixlen wins
    prefixes.sort(key=lambda p: (p.network_address, p.prefixlen))

    # Split prefix list into aggregatable chunks
    aggregatables = find_aggregatables(prefixes)

    # Aggregate aggregatables
    for aggregatable in aggregatables:
        yield from aggregate_aggregatable(aggregatable, debug)
