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


from ipaddress import IPv4Network, IPv6Network, ip_network
import logging
from typing import Union, List, Iterator


LOGGER = logging.getLogger(__name__)


def find_aggregatables(prefixes: List[Union[IPv4Network, IPv6Network]]) -> Iterator:
    """
    Split prefix lists into aggregatable chunks

    Parameters:
    -----------
    prefixes: list
        Sorted list of IPv4 or IPv6 prefixes serialized as either IPv4Network or IPv6Network

    Returns
    -------
    generator:
        Iterable made of sorted list of aggregatable IPv4 or IPv6 prefixes serialized as either
        IPv4Network or IPv6Network
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


def aggregate_aggregatable(
    aggregatable: List[Union[IPv4Network, IPv6Network]]
) -> Iterator[Union[IPv4Network, IPv6Network]]:
    """
    Aggregates aggregatable chunks

    Parameters:
    -----------
    aggregatable : list
        Sorted list of aggregatable IPv4 or IPv6 prefixes serialized as either IPv4Network or
        IPv6Network

    Returns
    -------
    generator:
        Aggregates serialized as either IPv4Network or IPv6Network
    """
    LOGGER.debug('Aggregatables: %s',  ', '.join(map(str, aggregatable)))
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
            LOGGER.debug('  Skipping: %s', prefix)
            continue
        LOGGER.debug(' Prefix: %s', prefix)

        # Iteratively reduce aggregate length
        for tentative_len in range(prefix.prefixlen, -1, -1):
            tentative = ip_network(
                f'{prefix.network_address}/{tentative_len}', False
            )
            LOGGER.debug('  Tentative aggregate: %s', tentative)
            # If boundaries are exceeded, then exit the loop
            if prefix.network_address != tentative.network_address or \
                tentative.broadcast_address > aggregatable_end:
                LOGGER.debug('  Boundaries exceeded by netmask: /%d', tentative_len)
                break

            # At the end of every loop, consider the update aggregate to current length
            aggregate = tentative
            aggregate_end = aggregate.broadcast_address

        # Return aggregate
        LOGGER.debug(' Aggregate found: %s', aggregate)
        yield aggregate


def aggregate_prefixes(
    prefixes: List[Union[str, IPv4Network, IPv6Network]],
    max_length: int = 128,
    truncate: int = False,
) -> Iterator[Union[IPv4Network, IPv6Network]]:
    """
    Aggregates IPv4 or IPv6 prefixes.

    Gets a list of unsorted IPv4 or IPv6 prefixes and returns a sorted iterable of aggregates.

    Parameters
    ----------
    prefixes : list
        Unsorted list of IPv4 or IPv6 prefixes serialized as either string, IPv4Network or
        IPv6Network
    max_length: int
        Discard longer prefixes prior to processing
    truncate: int
        Truncate IP/mask to network/mask

    Returns
    -------
    generator
        Sorted iterable of IPv4 or IPv6 aggregated prefixes serialized as either IPv4Network
        or IPv6Network
    """

    # Translate prefixes into a parsable data structure and discard those that exceed maxlen
    filtered_prefixes = []
    for prefix in prefixes:
        prefix = ip_network(prefix, False)
        if prefix.prefixlen <= max_length:
            filtered_prefixes.append(prefix)
    prefixes = filtered_prefixes

    # Apply truncate
    if truncate:
        prefixes = [
            ip_network(f'{prefix.network_address}/{truncate}', False)
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
        yield from aggregate_aggregatable(aggregatable)
