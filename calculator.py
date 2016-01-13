import re
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


@app.route('/<n>/')
def calculate(n):
    n = WHITESPACE_REGEX_PAT.sub('', n)
    n = SUBTRACT_REGEX_PAT.sub('-', n)
    n = n.replace('--', '+')
    answer = _calculate(n)

    if IS_SERVER:
        return jsonify({
            "answer": answer
        })
    else:
        return answer


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
        m = parts.pop(0)

        while parts:
            m = op['func'](m, parts.pop(0))

        return m

    if '.' in n:
        return float(n)

    return int(n)


@app.route("/<operation>/<n>/<m>/")
def request_answer(operation, n, m):
    answer = eval("%s('%s', '%s')" % (operation, n, m))
    return jsonify({
        operation: answer
    })


def can_perform(func):
    def _func(n, m):
        if (not IS_SERVER) or func.__name__ in CAN_PERFORM:
            return func(n, m)
        else:
            return request_answer(func.__name, n, m)

    return _func


@can_perform
def multiply(n, m):
    return _calculate(n) * _calculate(m)


@can_perform
def add(n, m):
    return _calculate(n) + _calculate(m)


@can_perform
def subtract(n, m):
    return _calculate(n) - _calculate(m)


@can_perform
def divide(n, m):
    return _calculate(n) / _calculate(m)


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
