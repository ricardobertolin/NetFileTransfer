import ast
import socket
import sys
import time
import os
from tqdm import tqdm
from protocol_logger import ProtocolLogger, print_header

HOST = '127.0.0.1'
PORT = 9999
DATA_PORT = 9998
DIRECTORY = 'OFFBOUNDS'


def Upload(filename, conn):
    size = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        with tqdm(total=size, unit='B', unit_scale=True, desc='  Uploading', ncols=60) as pbar:
            for chunk in iter(lambda: f.read(1000), b''):
                conn.send(chunk)
                pbar.update(len(chunk))


# ── setup ────────────────────────────────────────────────────────────────────

pydir = os.path.dirname(os.path.realpath(__file__))
os.chdir(pydir)
print_header('UPLOAD', HOST, HOST, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
log = ProtocolLogger(s)

try:
    s.connect((HOST, PORT))
    log.connect_event(HOST, PORT)
except Exception as e:
    log.event(f'Connection failed: {e}')
    sys.exit()

# ── phase 1: discover / create remote directory ───────────────────────────────

log.send(bytes('os.listdir()\n', 'utf-8'))
time.sleep(2)
response = log.recv(2048).decode()

if DIRECTORY not in response:
    log.event(f"Directory '{DIRECTORY}' not found on server — creating it")
    log.send(bytes('os.makedirs({})\n'.format(DIRECTORY), 'utf-8'))
    time.sleep(2)
    log.recv(2048)
else:
    log.event(f"Directory '{DIRECTORY}' found — listing its contents")
    log.send(bytes('os.listdir({})\n'.format(DIRECTORY), 'utf-8'))
    time.sleep(2)
    response = log.recv(2048).decode()
    response = ast.literal_eval(response)

# ── phase 2: choose a local file ─────────────────────────────────────────────

print()
print('Local directory:', os.getcwd())
print('Local files:    ', os.listdir())
print()

while True:
    filename = input('Enter the filename to transfer (or press ENTER to quit): ')
    if not filename:
        sys.exit()
    elif filename in response:
        print('This file already exists on the server.')
    elif not os.path.isfile(filename):
        print('This file does not exist locally.')
    else:
        log.event(f"File selected: '{filename}'")
        break

# ── phase 3: open data channel and trigger upload ────────────────────────────

log.event(f'Opening data channel listener on port {DATA_PORT} ...')
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s2.bind(('', DATA_PORT))
    s2.listen(1)
except Exception as e:
    log.event(f'Bind failed: {e}')
    sys.exit()

log.send(bytes('upload({}\\{})\n'.format(DIRECTORY, filename), 'utf-8'))

conn, addr = s2.accept()
log.data_channel_event(DATA_PORT)

# ── phase 4: transfer ────────────────────────────────────────────────────────

Upload(filename, conn)
conn.close()
s2.close()
log.event('Transfer complete!')
input('\nPress ENTER to exit')
