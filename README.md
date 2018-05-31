# aggregate-prefixes
Fast IPv4 and IPv6 prefix aggregator written in Pyrhon.  

Gets a list of unsorted IPv4 or IPv6 prefixes from argument or SDTIN and returns a sorted list of aggregates to STDOUT
Errors go to STDERR.

## CLI Syntax for executable
<pre>
usage: aggregate-prefixes [-h] [--max-length [LENGTH]] [--verbose] [--version]
                          prefixes

Aggregates IPv4 or IPv6 prefixes from file or STDIN

positional arguments:
  prefixes              Unsorted list of IPv4 or IPv6 prefixes. Use '-' for
                        STDIN.

optional arguments:
  -h, --help            show this help message and exit
  --max-length [LENGTH], -m [LENGTH]
                        Discard longer prefixes prior to processing
  --verbose, -v         Display verbose information about the optimisations
  --version, -V         show program's version number and exit

</pre>

# Usage as module
```
$ python
Python 2.7.14+ (default, Apr  2 2018, 04:16:25) 
[GCC 7.3.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>>
>>> from aggregate_prefixes.aggregate_prefixes import aggregate_prefixes
>>> aggregate_prefixes(['192.0.2.0/32', '192.0.2.1/32', '192.0.2.2/32'])
['192.0.2.0/31', '192.0.2.2/32']
>>> 
```

# Python compatibility
Tested with:
 - Python 2.7.15
 - Python 3.6.5
