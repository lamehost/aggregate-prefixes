# -*- coding: utf-8 -*-

"""
Provides core functions for package aggregate-prefixes
"""

from __future__ import absolute_import

import ipaddr


def aggregate_prefixes(prefixes):
    """
    Aggregates IPv4 or IPv6 prefixes.

    Gets a list of unsorted IPv4 or IPv6 prefixes and returns a sorted list of aggregates.

    Parameters
    ----------
    prefixes : list
        Unsorted list of IPv4 or IPv6 prefixes serialized as strings or ipaddr objects

    Returns
    -------
    list
        Sorted list of IPv4 or IPv6 aggregated prefixes serialized as strings

    """
    aggregates = list()
    # Sort prefixes. Smaller network goes firt, on tie larger prefixlen wins
    prefixes = sorted(
        [ipaddr.IPNetwork(p) for p in prefixes], key=lambda p: (p.network, p.prefixlen)
    )
    # print "PREFIXES: %s" % ', '.join([str(_) for _ in prefixes])
    # print

    _id = 0
    total_prefixes = len(prefixes)
    while _id < total_prefixes:
        # print "LOOP START -->"
        # print
        prefix = prefixes[_id]
        # print "PREFIX: %s (Network: %s, Broadcast: %s)" % (prefix, prefix.network, prefix.broadcast)
        # Assuming current is the only contigous prefix in the list
        contigous_prefixes = [prefix]
        last_contigous = prefix

        # Find list of contigous prefixes
        next_id = _id + 1
        while next_id < total_prefixes:
            last_contigous = contigous_prefixes[-1]
            next_prefix = prefixes[next_id]
            # print "NEXT: %s (Network: %s, Broadcast: %s)" % (next_prefix, next_prefix.network, next_prefix.broadcast)
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
        # print

        # Move position forward to next non contigous prefix
        _id = next_id

        # Aggregate contigous prefixes
        contigous_id = 0
        total_contigous = len(contigous_prefixes)
        while contigous_id < total_contigous:
            # print "CONTIGOUS: %s" % ', '.join([str(_) for _ in contigous_prefixes[contigous_id:]])
            first_contigous = contigous_prefixes[contigous_id]
            # print "FIRST: %s (Network: %s, Broadcast: %s)" % (first_contigous, first_contigous.network, first_contigous.broadcast)
            # print "LAST: %s (Network: %s, Broadcast: %s)" % (last_contigous, last_contigous.network, last_contigous.broadcast)
            # Assume new aggregate is this contigous
            aggregate = first_contigous
            tentative_len = first_contigous.prefixlen
            while True:
                tentative_len -= 1
                # Calculate new tentative prefix
                tentative = ipaddr.IPNetwork('%s/%d' % (first_contigous.network, tentative_len))
                # print "TENTATIVE: %s (Network: %s, Broadcast: %s)" % (tentative, tentative.network, tentative.broadcast)
                # Stop loop if bit boundaries are exceeded
                if tentative.network != first_contigous.network \
                    or tentative.broadcast > last_contigous.broadcast:
                    break
                aggregate = tentative
            # Found a new aggregate
            # print "AGGREGATE: %s (Network: %s, Broadcast: %s)" % (aggregate, aggregate.network, aggregate.broadcast)
            aggregates.append(aggregate)
            # Find how many contigous the aggregate spans
            covered_id = contigous_id + 1
            while covered_id < total_contigous:
                # print "TESTING: %s (Network: %s, Broadcast: %s)" % (contigous_prefixes[covered_id], contigous_prefixes[covered_id].network, contigous_prefixes[covered_id].broadcast)
                if aggregate.broadcast < contigous_prefixes[covered_id].network:
                    break
                covered_id += 1
            # print "COVERED: %s " % ', '.join([str(_) for _ in contigous_prefixes[contigous_id:covered_id]])
            # print
            contigous_id = covered_id

        # print "<-- LOOP END"
    # print
    return ['%s/%d' % (a.network, a.prefixlen) for a in aggregates]
