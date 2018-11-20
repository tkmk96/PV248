from sys import argv
from csv import DictReader
from datetime import datetime, date
import re
import numpy
import json
import math


KEY_REGEX = re.compile(r"^(\d\d\d\d-\d\d-\d\d)\/(\d\d)$")
DATE_FORMAT = '%Y-%m-%d'
START_DATE = '2018-9-17'

def safe_eval(key):
    return KEY_REGEX.match(key.strip())


def get_average_data(csv_reader):
    data = {}
    data_avg = {}
    for line in csv_reader:
        for key, value in line.items():
            r_eval = safe_eval(key)
            if r_eval is None:
                continue
            if key not in data:
                data[key] = []
            data[key].append(float(value))

    for key, array in data.items():
        count = len(array)
        number = 0.0
        for n in array:
            number += n
        data_avg[key] = number / count
    return data_avg


def get_student_data(csv_reader, student_id):
    data_student = {}
    for line in csv_reader:
        if line['student'] == student_id:
            for key, value in line.items():
                r_eval = safe_eval(key)
                if r_eval is None:
                    continue
                data_student[key] = float(value)
    return data_student


def get_points(data):
    by_date = {}
    by_exercise = {}

    for key, value in data.items():
        r_eval = safe_eval(key)
        if r_eval is None:
            continue
        datum = r_eval.group(1)
        exercise = r_eval.group(2)

        if datum not in by_date:
            by_date[datum] = float(value)
        else:
            by_date[datum] += float(value)

        if exercise not in by_exercise:
            by_exercise[exercise] = float(value)
        else:
            by_exercise[exercise] += float(value)

    return by_date, by_exercise


def get_points_array(points_dict):
    array = []
    for key, value in points_dict.items():
        array.append(value)
    return array


def get_points_by_date_sorted(by_date):
    array = []

    for key, value in by_date.items():
        array.append({
            'date': key,
            'points': value
        })

    return sorted(array, key=lambda x: x['date'])


def get_start_date():
    return datetime.strptime(START_DATE, DATE_FORMAT).date().toordinal()


def get_regression_slope(sorted_points, start_date):
    dates = []
    points = []
    dates_counted = []
    acc_points = []

    for d in sorted_points:
        dates.append(datetime.strptime(d['date'], DATE_FORMAT).date().toordinal())
        points.append(d['points'])

    acc_points.append(points[0])

    for i in range(1, len(points)):
        acc_points.append(acc_points[i - 1] + points[i])

    for dt in dates:
        dates_counted.append(dt - start_date)
    return numpy.linalg.lstsq([[dt] for dt in dates_counted], acc_points, rcond=-1)[0][0]


def get_stat_data(points_array, start_date, regression_slope, ):
    date16 = date20 = 'inf'
    if regression_slope != 0:
        date16 = date.fromordinal(math.ceil((16.0 / regression_slope) + start_date)).isoformat()
        date20 = date.fromordinal(math.ceil((20.0 / regression_slope) + start_date)).isoformat()

    stats = {
        'mean': numpy.mean(points_array),
        'median': numpy.median(points_array),
        'passed': numpy.count_nonzero(points_array),
        'total': sum(points_array),
        'regression slope': regression_slope,
        'date 16': date16,
        'date 20': date20,
    }

    return stats


def main():
    csv_file = argv[1]
    student_id = argv[2]
    file = open(csv_file, encoding="utf8")
    csv_reader = DictReader(file)

    if student_id != 'average':
        data = get_student_data(csv_reader, student_id)
    else:
        data = get_average_data(csv_reader)

    by_date, by_exercise = get_points(data)

    sorted_points_array_dict = get_points_by_date_sorted(by_date)
    start_date = get_start_date()
    regression_slope = get_regression_slope(sorted_points_array_dict, start_date)

    stats = get_stat_data(get_points_array(by_exercise), start_date, regression_slope)
    print(json.dumps(stats, indent=4))
    file.close()


if __name__ == '__main__':
    main()
