#!/usr/bin/env python3
import socket
import sys
import threading
import mmonitor

threading.Thread(target=mmonitor.Console).start()

porta = int(input('Porta para ouvir sensores: '))
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mmonitor.SOCKETUDP = s

try:
    s.bind(('', porta))
except:
    print('# erro de bind')
    sys.exit()

mmonitor.TrataSensor()

print('o servidor encerrou!')
s.close()
