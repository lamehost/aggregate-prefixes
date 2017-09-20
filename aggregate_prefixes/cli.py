#!/usr/bin/python

import ipaddr
import fileinput
import sys


def aggregate_prefixes(prefixes):
	aggregates=list()
	try:
		prefixes=sorted([ipaddr.IPNetwork(p) for p in prefixes], key=lambda p: p.network)
	except Exception, e:
		print e
		sys.exit()
	larger=prefixes[0]
	starting_prefixlen = larger.prefixlen
	for prefix in prefixes[1:]:
		# Aggregate prefixes of the same legnth, if possible
		if (starting_prefixlen == prefix.prefixlen) and larger.broadcast+1 == prefix.network:
			prefixlen=larger.prefixlen-1
			while True:
				# Calculate new tentative prefix
				tentative=ipaddr.IPNetwork('%s/%d' % (larger.network, prefixlen))
				# Check bit boundaries
				if tentative.network != larger.network:
					break
				if tentative.Contains(prefix):
					larger=tentative
					break
				prefixlen=larger_prefixlen-1
		# Next if prefix is smaller than the current larger one
		if larger.broadcast >= prefix.broadcast:
			continue
		# Save larger if network value changes
		if larger.network != prefix.network:
				aggregates.append(larger)
		larger=prefix
		starting_prefixlen=prefix.prefixlen
	# Handle the last larger prefix
	if not len(aggregates) or not aggregates[-1].Contains(larger):
		aggregates.append(larger)
	return ['%s/%d' % (a.network, a.prefixlen) for a in aggregates]


def main():
	prefixes=set([_.strip() for _ in fileinput.input()])
	print '\n'.join([_ for _ in aggregate_prefixes(prefixes)])


if __name__ == '__main__':
	main()
