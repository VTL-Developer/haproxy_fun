import re
from copy import deepcopy
from flask import Flask, jsonify
from werkzeug.routing import BaseConverter

app = Flask(__name__)
WHITESPACE_REGEX_PAT = re.compile(r'\s')
SUBTRACT_REGEX_PAT = re.compile(r'-\+|\+-')
IS_SERVER = False
CAN_PERFORM = []


class RegexConverter(BaseConverter):

    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


def get_pid():
    return 1  # TODO: Get the proper PID


@app.route('/<n>/')
def calculate(n):
    n = WHITESPACE_REGEX_PAT.sub('', n)
    n = SUBTRACT_REGEX_PAT.sub('-', n)
    n = n.replace('--', '+')
    answer = _calculate(n)

    if IS_SERVER:
        answer = jsonify({
            'answer': answer['answer'],
            'pid': get_pid(),
            'stack': answer['stack'],
            'values': n,
            'operation': 'calculate',
        })

    return answer


def parse_answer(func):
    def _func(n):
        answer = func(n)
        if IS_SERVER and type(answer) not in [str, unicode, dict]:
            return {
                'answer': answer,
                'stack': [],
                'values': answer,
                'operation': 'none',
                'pid': get_pid(),
            }

        return answer

    return _func


@parse_answer
def _calculate(n):
    global OPERATORS
    if not n:
        return 0

    if type(n) not in [str, unicode]:
        return n

    for op in OPERATORS:
        if op['symbol'] not in n:
            continue

        parts = n.split(op['symbol'])
        values = deepcopy(parts)
        stack = []
        m = parts.pop(0)

        while parts:
            if IS_SERVER:
                stack.append(op['func'](m, parts.pop(0)))
                m = stack[-1]['answer']
            else:
                m = op['func'](m, parts.pop(0))

        if IS_SERVER:
            return {
                'answer': m,
                'stack': stack,
                'values': values,
                'operation': op['func'].__name__,
            }
        return m

    if '.' in n:
        return float(n)

    return int(n)


@app.route("/<operation>/<n>/<m>/")
def request_answer(operation, n, m):
    return eval("%s('%s', '%s')" % (operation, n, m))


def can_perform(func):
    def _func(n, m):
        n, m = _calculate(n), _calculate(m)
        if not IS_SERVER:
            return func(n, m)
        elif func.__name__ in CAN_PERFORM:
            answer = func(n['answer'], m['answer'])
            return {
                'answer': answer,
                'stack': [n['stack'], m['stack']],
                'values': [n['answer'], m['answer']],
                'operation': func.__name__,
            }
        else:
            return request_answer(func.__name__, n, m)

    return _func


@can_perform
def multiply(n, m):
    return n * m


@can_perform
def add(n, m):
    return n + m


@can_perform
def subtract(n, m):
    return n - m


@can_perform
def divide(n, m):
    return n / m


OPERATORS = [
    {'symbol': '+', 'func': add, },
    {'symbol': '-', 'func': subtract, },
    {'symbol': '*', 'func': multiply, },
    {'symbol': 'd', 'func': divide, },
]


if __name__ == "__main__":
    IS_SERVER = True
    CAN_PERFORM = ["add", "multiply", "subtract", "divide"]
    app.run(debug=True)
