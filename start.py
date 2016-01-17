from ConfigParser import SafeConfigParser
import subprocress32

options = ['add', 'multiply', 'subtract', 'divide']
scp = SafeConfigParser()
scp.read('haproxy.ini')
servers = []
servers_that_support = []

for sec in scp.sections():
    if sec.lower().startswith('server_'):
        servers.append({opt: scp.get(sec, opt) for opt in options})

for s in servers:
    process_call = "python calculator.py %s" % (" ".join([
        ("--%s %s") % (k, v) for k, v in s]))

for opt in options:
    servers_that_support[opt] = []  # TODO: some filter option
    assert len(servers_that_support[opt]), ("A server is needed to support %s"
                                            % opt)
