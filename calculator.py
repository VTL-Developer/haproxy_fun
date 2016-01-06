import re

WHITESPACE_REGEX_PAT = re.compile(r'\s')
SUBTRACT_REGEX_PAT = re.compile(r'-\+|\+-')


def calculate(n):
    n = WHITESPACE_REGEX_PAT.sub('', n)
    n = SUBTRACT_REGEX_PAT.sub('-', n)
    n = n.replace('--', '+')

    return _calculate(n)


def _calculate(n):
    global OPERATORS
    if not n:
        return 0

    if not type(n) is str:
        return n

    for op in OPERATORS:
        if op['symbol'] not in n:
            continue

        parts = n.split(op['symbol'])
        m = parts.pop(0)

        while parts:
            m = op['func'](m, parts.pop(0))

        return m

    if '.' in n:
        return float(n)

    return int(n)


def multiply(n, m):
    return _calculate(n) * _calculate(m)


def add(n, m):
    return _calculate(n) + _calculate(m)


def subtract(n, m):
    return _calculate(n) - _calculate(m)


def divide(n, m):
    return _calculate(n) / _calculate(m)


OPERATORS = [
    {'symbol': '+', 'func': add, },
    {'symbol': '-', 'func': subtract, },
    {'symbol': '*', 'func': multiply, },
    {'symbol': '/', 'func': divide, },
]
