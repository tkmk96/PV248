import sys
import re


def add_value(dict, key):
    if dict.get(key) is not None:
        dict[key] += 1
    else:
        dict[key] = 1


def calc_composers(f):
    r = re.compile(r"Composer: (.*)")
    composers = {}
    for line in f:
        m = r.match(line)
        if m is None: continue
        temp_composers = m.group(1).split(';')
        for composer in temp_composers:
            composer_name = re.sub(r'\([+\d].*\)', '', composer).strip()
            if composer_name != "":
                add_value(composers, composer_name)
    return composers


def print_composers(composers):
    print(composers.__len__())
    for composer, count in composers.items():
        print(composer + ": %d" % count)


def get_century(year_text):
    year = int(year_text) - 1
    year = year // 100
    year = year + 1
    return year


def print_centuries(centuries):
    for century, count in centuries.items():
        print("%dth century: %d" % (century, count))


def calc_centuries(f):
    r = re.compile(r"Composition Year:.*(\d{4}|(\d{2})th century)")
    centuries = {}
    for line in f:
        m = r.match(line)
        if m is not None:
            parsed_century = re.findall(r'\d+', m.group(1))[0]
            if parsed_century.__len__() == 4:
                century_number = get_century(parsed_century)
            else:
                century_number = int(parsed_century)
            add_value(centuries, century_number)
    return centuries


filename = sys.argv[1]
method = sys.argv[2]

f = open(filename, encoding="utf8")

if method == "composer":
    print_composers(calc_composers(f))
elif method == "century":
    print_centuries(calc_centuries(f))
else:
    print("Error: entered command '" + method + "' is not supported")
