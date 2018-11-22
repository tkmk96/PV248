from sys import argv
import re
import numpy
from csv import DictReader
import json


KEY_REGEX = re.compile(r"^(\d\d\d\d-\d\d-\d\d)\/(\d\d)$")


def safe_eval(key):
    return KEY_REGEX.match(key.strip())


def mode_dates(csv_reader):
    data = {}
    for line in csv_reader:
        line_data = {}
        for key, value in line.items():
            r_eval = safe_eval(key)
            if r_eval is None:
                continue
            date = r_eval.group(1)
            if date not in line_data:
                line_data[date] = float(value)
            else:
                line_data[date] += float(value)
        for key, value in line_data.items():
            if key not in data:
                data[key] = []
            data[key].append(value)
    return data


def mode_deadlines(csv_reader):
    data = {}
    for line in csv_reader:
        line_data = {}
        for key, value in line.items():
            if safe_eval(key) is None:
                continue
            if key not in line_data:
                line_data[key] = float(value)
            else:
                line_data[key] += float(value)
        for key, value in line_data.items():
            if key not in data:
                data[key] = []
            data[key].append(value)
    return data


def mode_exercises(csv_reader):
    data = {}
    for line in csv_reader:
        line_data = {}
        for key, value in line.items():
            r_eval = safe_eval(key)
            if r_eval is None:
                continue
            exercise = r_eval.group(2)
            if exercise not in line_data:
                line_data[exercise] = float(value)
            else:
                line_data[exercise] += float(value)
        for key, value in line_data.items():
            if key not in data:
                data[key] = []
            data[key].append(value)
    return data


def read_csv(csv_reader, mode):
    data = {}
    if mode == 'dates':
        data = mode_dates(csv_reader)
    elif mode == 'deadlines':
        data = mode_deadlines(csv_reader)
    elif mode == 'exercises':
        data = mode_exercises(csv_reader)
    return data


def get_stat_data(data):
    stats = {}
    for key, array in data.items():
        stats[key] = {
            'mean': numpy.mean(numpy.array(array)),
            'median': numpy.median(numpy.array(array)),
            'passed': numpy.count_nonzero(numpy.array(array)),
            'first': numpy.percentile(numpy.array(array), 25),
            'last': numpy.percentile(numpy.array(array), 75),
        }
    return stats


def main():
    csv_file = argv[1]
    mode = argv[2]
    file = open(csv_file, encoding="utf8")
    csv_reader = DictReader(file)
    data_dict = read_csv(csv_reader, mode)
    stats = get_stat_data(data_dict)
    print(json.dumps(stats, indent=4))
    file.close()


if __name__ == '__main__':
    main()