import socket
import threading
import os
import sys
from pathlib import Path


def read_line(conn):
    """Read one newline-terminated command from the control socket."""
    line = ''
    while True:
        try:
            byte = conn.recv(1)
        except Exception:
            print('Client disconnected unexpectedly.')
            return 0
        if not byte:
            return 0
        byte = byte.decode()
        if byte == '\r':
            continue
        if byte == '\n':
            break
        line += byte
    return line


def upload(conn, ip, filepath):
    """Receive a file from the client over the data channel."""
    try:
        f = open(filepath, 'wb')
    except Exception as e:
        print('Error opening file for writing:', e)
        conn.send(b'DATA PORT NOT OPEN\n')
        return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, 9998))
        while True:
            data = s.recv(1024)
            if not data:
                break
            f.write(data)
        f.close()
        s.close()
        conn.send(b'TRANSFER COMPLETE\n')
    except Exception as e:
        print('Upload error:', e)
        f.close()
        conn.send(b'DATA PORT NOT OPEN\n')


def download(conn, ip, filepath):
    """Send a file to the client over the data channel."""
    try:
        f = open(Path(filepath), 'rb')
    except Exception as e:
        print('Error opening file for reading:', e)
        conn.send(b'DATA PORT NOT OPEN\n')
        return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, 9998))
        for chunk in iter(lambda: f.read(1024), b''):
            s.send(chunk)
        f.close()
        s.close()
        conn.send(b'TRANSFER COMPLETE\n')
    except Exception as e:
        print('Download error:', e)
        f.close()
        conn.send(b'DATA PORT NOT OPEN\n')


def handle_client(conn, addr):
    """Handle all commands from a single connected client."""
    print(f'Handling client {addr}')
    while True:
        conn.send(b'\r\n')
        data = read_line(conn)
        print(f'{addr} sent: {data!r}')
        if data == 0:
            break
        try:
            if data == 'os.getcwd()':
                conn.send(os.getcwd().encode())

            elif data.startswith('os.listdir'):
                path = data.split('(')[1].split(')')[0].strip() or '.'
                result = os.listdir(path)
                conn.send(str(result).encode())

            elif data.startswith('os.makedirs'):
                path = data.split('(')[1].split(')')[0].strip()
                if path:
                    os.makedirs(path, exist_ok=True)
                    print('Created directory:', path)
                    conn.send(b'OK')
                else:
                    conn.send(b'NOK')

            elif data.startswith('upload'):
                filepath = data.split('(')[1].split(')')[0]
                upload(conn, addr[0], filepath)

            elif data.startswith('download'):
                filepath = data.split('(')[1].split(')')[0]
                download(conn, addr[0], filepath)

            else:
                print('Unknown command:', repr(data))
                conn.send(b'UNKNOWN COMMAND')

        except Exception as e:
            print('Error handling command:', e)
            conn.send(b'UNKNOWN ERROR\n')

    print(f'{addr} disconnected.')


# ── main ─────────────────────────────────────────────────────────────────────

print('Simple File Transfer Protocol Server')
print()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('', 9999))
except Exception as e:
    print('Bind error:', e)
    sys.exit()

s.listen(5)

print('Listening on port 9999')
print('Control channel:   client -----> server [9999]')
print('Data channel:      server -----> client [9998]  (reverse connection)')
print()

while True:
    conn, addr = s.accept()
    print(f'Accepted connection from {addr}')
    t = threading.Thread(target=handle_client, args=(conn, addr))
    t.start()
