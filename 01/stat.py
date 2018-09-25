import sys
import re

def addOrCreate(dict, key):
    if dict.has_key(key):
        dict[key] += 1
    else:
        dict[key] = 1

def findComposers(f):
    r = re.compile(r"Composer: (.*)")
    composers = {}
    for line in f:
        m = r.match(line)
        if m is None: continue
        addOrCreate(composers, m.group(1))
    return composers

def composer(f):
    print findComposers(f)
    

def centuries(f):
    print "centuries"

filename = sys.argv[1]
method = sys.argv[2]

f = open(filename, 'r')

if method == "composer":
    composer(f)
else:
    centuries(f)



    
