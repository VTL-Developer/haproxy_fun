import re
from copy import deepcopy
from flask import Flask, jsonify
from argparse import ArgumentParser
from werkzeug.routing import BaseConverter

app = Flask(__name__)
WHITESPACE_REGEX_PAT = re.compile(r'\s')
SUBTRACT_REGEX_PAT = re.compile(r'-\+|\+-')
IS_SERVER = False
CAN_PERFORM = []
SERVER_PROXY = "http://localhost:8000/"


def get_pid():
    return 1  # TODO: Get the proper PID


@app.route('/calculate/<n>/')
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
    return jsonify(eval("%s('%s', '%s')" % (operation, n, m)))


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
    parser = ArgumentParser()
    parser.add_argument("--add", dest="add", default=1, type=int)
    parser.add_argument("--multiply", dest="multiply", default=1, type=int)
    parser.add_argument("--subtract", dest="subtract", default=1, type=int)
    parser.add_argument("--divide", dest="divide", default=1, type=int)
    parser.add_argument("--port", dest="port", default=8000, type=int)
    opts = parser.parse_args()
    if opts.add:
        CAN_PERFORM.append('add')

    if opts.subtract:
        CAN_PERFORM.append('subtract')

    if opts.multiply:
        CAN_PERFORM.append('multiply')

    if opts.divide:
        CAN_PERFORM.append('divide')

    app.run(debug=True, port=opts.port)
