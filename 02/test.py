from sys import argv
from scorelib import load

results = load(argv[1])

for p in results:
    p.format()
    print("")

