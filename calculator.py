import re
from copy import deepcopy
from flask import Flask, jsonify
from argparse import ArgumentParser
from urlparse import urljoin
from requests import get
from json import loads as json_loads
from os import getpid

app = Flask(__name__)
WHITESPACE_REGEX_PAT = re.compile(r'\s')
SUBTRACT_REGEX_PAT = re.compile(r'-\+|\+-')
IS_SERVER = False
CAN_PERFORM = []
SERVER_PROXY = "http://localhost:8000/"
SERVER_PORT = 8000


@app.route('/calculate/<n>/')
def calculate(n):
    n = WHITESPACE_REGEX_PAT.sub('', n)
    n = SUBTRACT_REGEX_PAT.sub('-', n)
    n = n.replace('--', '+')
    answer = _calculate(n)

    if IS_SERVER:
        answer = jsonify({
            'answer': answer['answer'],
            'pid': getpid(),
            'stack': answer['stack'],
            'values': n,
            'operation': 'calculate',
            'port': SERVER_PORT,
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
                'pid': getpid(),
                'port': SERVER_PORT,
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
                'pid': getpid(),
                'port': SERVER_PORT,
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
        if not IS_SERVER:
            return func(n, m)
        else:
            n, m = _calculate(n), _calculate(m)

            if func.__name__ in CAN_PERFORM:
                answer = func(n['answer'], m['answer'])
                return {
                    'answer': answer,
                    'stack': [n['stack'], m['stack']],
                    'values': [n['answer'], m['answer']],
                    'operation': func.__name__,
                    'pid': getpid(),
                    'port': SERVER_PORT,
                }
            else:
                url_part = "%s/%s/%s/" % (func.__name__, n['answer'],
                                          m['answer'])
                answer = json_loads(get(urljoin(SERVER_PROXY,url_part)).content)
                answer['stack'] = [n, m]
                return answer

    _func.name = func.__name__

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

    SERVER_PORT = opts.port
    app.run(debug=True, port=opts.port,threaded=True)
