import sys
import re


def add_composer(dict, key):
    if dict.get(key) is not None:
        dict[key] += 1
    else:
        dict[key] = 1


def find_composers(f):
    r = re.compile(r"Composer: (.*)")
    composers = {}
    for line in f:
        m = r.match(line)
        if m is None: continue
        temp_composers = m.group(1).split(';')
        for composer in temp_composers:
            composer_name = re.sub(r'\([+\d].*\)', '', composer).strip()
            if composer_name != "":
                add_composer(composers, composer_name)
    return composers


def print_composers(composers):
    print(composers.__len__())
    for composer, count in composers.items():
        print(composer + ": %d" % count)


def composer(f):
    print_composers(find_composers(f))


def centuries(f):
    print("centuries")


filename = sys.argv[1]
method = sys.argv[2]

f = open(filename, encoding="utf8")

if method == "composer":
    composer(f)
else:
    centuries(f)



    
