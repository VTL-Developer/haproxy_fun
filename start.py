from ConfigParser import SafeConfigParser
import subprocess
from time import sleep
from jinja2 import Environment, PackageLoader

options = ['add', 'multiply', 'subtract', 'divide']
scp = SafeConfigParser()
scp.read('haproxy.ini')
servers = []
servers_that_support = {}
processes = []
PORT = 8000
PORT_OFFSET = 1

for sec in scp.sections():
    if sec.lower().startswith('server_'):
        settings = {opt: scp.get(sec, opt) for opt in options}
        settings['port'] = str(PORT_OFFSET + PORT)
        servers.append(settings)
        PORT_OFFSET += 1

for opt in options:
    servers_that_support[opt] = [s for s in servers if s[opt]]
    assert len(servers_that_support[opt]), ("A server is needed to support %s"
                                            % opt)

env = Environment(loader=PackageLoader('templates', '.'))
template = env.get_template('haproxy.cfg.temp')
with open('haproxy.cfg', 'wb') as f:
    f.write(template.render(operations=servers_that_support, servers=servers))

for s in servers:
    process_call = ["python", "calculator.py"]
    for key in s:
        process_call.extend(["--%s" % key, s[key]])
    processes.append(subprocess.Popen(process_call))

processes.append(subprocess.Popen(["haproxy", "-f", "haproxy.cfg"]))

try:
    sleep(3600)
except:
    pass
finally:
    for p in processes:
        p.kill()
