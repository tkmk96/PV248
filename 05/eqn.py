from sys import argv
from numpy import linalg
import re
import copy


EQ_REGEX = re.compile(r"(\d*)(.)")
VAR_REGEX = re.compile(r"[a-z]")


def parse_text(text):
    EQ_REGEX = re.compile(r"(\d*)(.)")
    equations = []

    for line in text.split('\n'):
        if line == '':
            continue
        sides = line.split('=')
        right_side = sides[1]
        left_side = sides[0].split(' ')
        left_side.insert(0, '+')

        variables = {}
        for i in range(0, left_side.__len__() - 1, 2):
            match = EQ_REGEX.search(left_side[i + 1])
            number = 1
            if match.group(1):
                number = int(match.group(1).strip())
            if left_side[i] == '-':
                number *= -1
            variable = match.group(2).strip()
            variables[variable] = number
        eq = {
            'variables': variables,
            'result': int(right_side.strip())
        }
        equations.append(eq)
    return equations


def get_all_variables(text):
    all_vars = VAR_REGEX.findall(text)
    return sorted(set(all_vars))


def normalize_equations(all_vars, equations):
    for equation in equations:
        for v in all_vars:
            if equation['variables'].get(v) is None:
                equation['variables'][v] = 0


def get_full_matrix(left_matrix, results):
    full_matrix = copy.deepcopy(left_matrix)
    for i in range(0, results.__len__()):
        full_matrix[i].append(results[i])
    return full_matrix


def get_matrices(equations):
    left_matrix = []
    results = []
    for eq in equations:
        results.append(eq['result'])
        matrix_line = []
        for v in sorted(eq['variables']):
            matrix_line.append(eq['variables'][v])
        left_matrix.append(matrix_line)
    full_matrix = get_full_matrix(left_matrix, results)
    return left_matrix, results, full_matrix


def get_result(left_matrix, results, full_matrix, all_vars):
    left_matrix_rank = linalg.matrix_rank(left_matrix)
    full_matrix_rank = linalg.matrix_rank(full_matrix)

    if left_matrix_rank != full_matrix_rank:
        return "no solution"

    try:
        result = linalg.solve(left_matrix, results)
        text_results = []
        for i, v in enumerate(all_vars):
            text_results.append(v + " = " + str(result[i]))
        return "solution: " + ", ".join(text_results)
    except:
        dimension = (len(all_vars) - left_matrix_rank)
        return "solution space dimension: %d" % dimension


text = open(argv[1], 'r', encoding="utf8").read()
equations = parse_text(text)
all_vars = get_all_variables(text)
normalize_equations(all_vars, equations)
left_matrix, results, full_matrix = get_matrices(equations)
print(get_result(left_matrix, results, full_matrix, all_vars))
