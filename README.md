#About

A playground set up for me to learn more about haproxy and load balancing, used with simple Python servers for calculating basic math operations, with some regard to ~~BE~~DMAS.

#Requirements

- Python 2.7.6+
- haproxy (I used version 1.4.24)
- pip
- Python packages specified by requirements.txt, you can install by `pip install -r requirements.txt`

#How to use

1. Run `python start.py` to start haproxy, and load all the servers specified in haproxy.ini
2. You can make HTTP calls to the following url: `http://localhost:8000/calculate/<problem>/`, where `<problem>` is a math problem that the server(s) try to solve. All integers and decimal points are accepted, and the following notations are used for specific math operations:
  - `+` for addition
  - `-` for subtraction
  - `*` for multiplication
  - `d` for division
3. See the HTTP response with a stack trace.

#How to add more servers

- Edit haproxy.ini to add more servers.
- Fill in a new server (as a new section) with the following: `[server_<unique_name>]`
- Fill in any options regarding the server with regards to `add`, `subtract`, `multiply`, `divide`. The corresponding value can be 0 (off) or 1 (on).
- Any missing option for the server would be assumed 1.
