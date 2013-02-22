#! /usr/bin/python

import json
import sys

"""
    crappy script to scan a log file and do simple counts
    of the data.

    counter.py {log_file} > {file.csv}

"""

f = open(sys.argv[1])
counts = {}
max_idle = 0
for line in f:
    if not 'fetch_query' in line:
        continue
    x, d = line.split('fetch_query :')
    data = json.loads(d)
    channel = data['channel']
    if not channel in counts:
        counts[channel]={}
    try:
        idle = int(data.get('idle', 0))
    except Exception, e:
        idle = 'err'
        pass
    if idle > 180 or idle < 0:
        idle = 'err'
    counts[channel][idle] = counts[channel].get(idle, 0) + 1

print "channel, idle, days"
for channel in counts.keys():
    if len(counts[channel]):
        keys = counts[channel].keys()
        keys.sort()
        for key in keys:
            print "%s,%s,%s" % (channel, key, counts[channel].get(key))
