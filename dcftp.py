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


def Download(path, conn):
    filename = os.path.basename(path)
    with open(filename, 'wb') as f:
        with tqdm(unit='B', unit_scale=True, desc='  Downloading', ncols=60) as pbar:
            while True:
                data = conn.recv(1000)
                if len(data) == 0:
                    break
                f.write(data)
                pbar.update(len(data))


def select_local_folder():
    print('Current directory:', os.getcwd())
    print('Directory contents:', os.listdir())
    folder = input('Choose a download folder (or press ENTER to keep the current one): ')
    if len(folder) > 0:
        try:
            if not os.path.isdir(folder):
                os.makedirs(folder)
            os.chdir(folder)
            print('Download folder:', os.getcwd())
        except Exception as e:
            print('Could not change folder:', e)
            print('Download folder:', os.getcwd())


def browse_remote_files(log):
    log.send(bytes('os.listdir()\n', 'utf-8'))
    time.sleep(2)
    response = log.recv(2048).decode()

    folder = input('Enter remote folder (or press ENTER to use root): ')

    if len(folder) > 0:
        if folder not in ast.literal_eval(response):
            print('That folder cannot be selected.')
        else:
            log.send(f'os.listdir({folder})\n'.encode())
            time.sleep(2)
            response = log.recv(2048).decode()

    filename = input('Select a file to download: ')
    if filename not in ast.literal_eval(response):
        print('File not found — selecting first available file.')
        filename = ast.literal_eval(response)[0]

    return os.path.join(folder, filename)


# ── setup ────────────────────────────────────────────────────────────────────

pydir = os.path.dirname(os.path.realpath(__file__))
os.chdir(pydir)
print_header('DOWNLOAD', HOST, HOST, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
log = ProtocolLogger(s)

try:
    s.connect((HOST, PORT))
    log.connect_event(HOST, PORT)
except Exception as e:
    log.event(f'Connection failed: {e}')
    sys.exit()

# ── phase 1: choose local download folder ────────────────────────────────────

log.event('Selecting local download folder ...')
select_local_folder()

# ── phase 2: browse server and pick a file ───────────────────────────────────

log.event('Browsing remote files ...')
remote = browse_remote_files(log)
if not remote:
    log.event('No remote file selected.')
    sys.exit()

log.event(f"File selected: '{remote}'")

# ── phase 3: open data channel and trigger download ──────────────────────────

log.event(f'Opening data channel listener on port {DATA_PORT} ...')
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s2.bind(('', DATA_PORT))
    s2.listen(1)
except Exception as e:
    log.event(f'Bind failed: {e}')
    sys.exit()

log.send('download({})\n'.format(remote).encode())

conn, addr = s2.accept()
log.data_channel_event(DATA_PORT)

# ── phase 4: receive file ────────────────────────────────────────────────────

Download(remote, conn)
conn.close()
s2.close()
log.event('Transfer complete!')
input('\nPress ENTER to exit')
s.close()
