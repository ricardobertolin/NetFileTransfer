import socket
import sys
import time

ESTADO = 'OFF'
IP_MONITOR = '255.255.255.255'
PORTA_MONITOR = 9999
ID = input('Entre com o nome do sensor: ')

def interpretaComando(comando, addr):
    global ESTADO
    strcomando = comando.decode().lower()
    strcomando = strcomando.replace('\n', '')
    print('Recebi o comando', strcomando)

    if strcomando == 'ligar':
        ESTADO = 'ON'
    elif strcomando == 'desligar':
        ESTADO = 'OFF'
    elif strcomando == 'consulta':
        s.sendto(('ESTADO ' + ESTADO).encode(), addr)
    else:
        print('comando desconhecido')

def registraSensor(s, ip, porta):
    s.sendto(('REGISTRO ' + ID).encode(), (ip, porta))
    s.setblocking(0)
    time.sleep(5)

    try:
        data, addr = s.recvfrom(1024)
        if data.decode() == 'ACKregistro':
            print('registrado no monitor ', addr)
            return True
        else:
            return False
    except:
        print('\no monitor está desligado')
        return False

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

while True:
    if registraSensor(s, IP_MONITOR, PORTA_MONITOR):
        break

count = 0
while True:
    time.sleep(1)

    try:
        data, addr = s.recvfrom(1024)
        interpretaComando(data, addr)
        count = 0
    except:
        count += 1

    if count >= 20:
        if registraSensor(s, '255.255.255.255', PORTA_MONITOR):
            count = 0
