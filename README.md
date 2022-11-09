# aggregate-prefixes
Fast IPv4 and IPv6 prefix aggregator written in Python.  

Gets a list of unsorted IPv4 or IPv6 prefixes from argument or SDTIN and returns a sorted list of aggregates to STDOUT
Errors go to STDERR.

## CLI Syntax for executable
<pre>
usage: aggregate-prefixes [-h] [--max-length [LENGTH]] [--truncate [MASK]]
                          [--verbose] [--version]
                          prefixes

Aggregates IPv4 or IPv6 prefixes from file or STDIN

positional arguments:
  prefixes              Text file of unsorted list of IPv4 or IPv6 prefixes.
                        Use '-' for STDIN.

optional arguments:
  -h, --help            show this help message and exit
  --max-length [LENGTH], -m [LENGTH]
                        Discard longer prefixes prior to processing
  --truncate [MASK], -t [MASK]
                        Ttruncate IP/mask to network/mask
  --verbose, -v         Display verbose information about the optimisations
  --version, -V         show program's version number and exit
</pre>

# Usage as module
```
$ python
Python 3.9.1+ (default, Feb  5 2021, 13:46:56) 
[GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
>>> from aggregate_prefixes import aggregate_prefixes
>>> list(aggregate_prefixes(['192.0.2.0/32', '192.0.2.1/32', '192.0.2.2/32']))
['192.0.2.0/31', '192.0.2.2/32']
>>> 
```

# Python compatibility
Tested with:
 - Python 3.7
 - Python 3.8
 - Python 3.9
 - Python 3.10
