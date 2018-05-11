from __future__ import absolute_import

import ipaddr


def aggregate_prefixes(prefixes):
    aggregates = list()
    # Sort prefixes. Smaller network goes firt, on tie larger prefixlen wins
    prefixes = sorted(
        [ipaddr.IPNetwork(p) for p in prefixes], key=lambda p: (p.network, p.prefixlen)
    )

    _id = 0
    total_prefixes = len(prefixes)
    while _id < total_prefixes:
        prefix = prefixes[_id]
        # Assuming current is the only contigous prefix in the list
        contigous_prefixes = [prefix]
        last_contigous = prefix

        # Find list of contigous prefixes
        next_id = _id+1
        for next_id in xrange(_id+1, total_prefixes):
            last_contigous = contigous_prefixes[-1]
            next_prefix = prefixes[next_id]
            # Current prefix is larger than next one
            if last_contigous.broadcast >= next_prefix.broadcast:
                continue
            # Next prefix is not contigous, loop ends here
            if last_contigous.broadcast+1 != next_prefix.network:
                break
            contigous_prefixes.append(next_prefix)

        # Aggregate contigous prefixes
        contigous_id = 0
        total_contigous = len(contigous_prefixes)
        while contigous_id < total_contigous:
            first_contigous = contigous_prefixes[contigous_id]
            # Assume new aggregate is this contigous
            aggregate = first_contigous
            tentative_len = first_contigous.prefixlen
            while True:
                tentative_len -= 1
                # Calculate new tentative prefix
                tentative = ipaddr.IPNetwork('%s/%d' % (first_contigous.network, tentative_len))
                # Stop loop if bit boundaries are exceeded
                if tentative.network != first_contigous.network \
                    or tentative.broadcast > last_contigous.broadcast:
                    break
                aggregate = tentative
            # Found a new aggregate
            aggregates.append(aggregate)
            # Find how many contigous the aggregate spans
            for new_contigous_id in xrange(contigous_id, total_contigous):
                if aggregate.broadcast < contigous_prefixes[new_contigous_id].network:
                    break
                contigous_id = new_contigous_id
            # Increment contigous
            contigous_id += 1

        _id = next_id

    return ['%s/%d' % (a.network, a.prefixlen) for a in aggregates]
