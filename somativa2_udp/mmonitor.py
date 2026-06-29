import sys

CONSOLE = None
SENSORES = {}
SOCKETUDP = None

def Console():
    global CONSOLE
    global SENSORES
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('', 8888))
    except:
        print('# erro de bind')
        sys.exit()
    s.listen(1)

    while True:
        conn, addr = s.accept()
        print('console ativado')
        CONSOLE = conn
        CONSOLE.send('Digite SENSOR_ID COMANDO\r\n'.encode())

        while True:
            data = CONSOLE.recv(200).decode()
            if not data:
                print('Console encerrou')
                CONSOLE = None
                break

            if len(data) < 4:
                # quebras de linha do Putty
                continue
            try:
                (sensor, comando) = data.split(' ', 1)
                if sensor in SENSORES:
                    SOCKETUDP.sendto(comando.encode(), SENSORES[sensor])
                else:
                    CONSOLE.send('Esse sensor nao existe\r\n'.encode())
            except:
                CONSOLE.send('Digite SENSOR_ID COMANDO\r\n'.encode())
            print(data)

def TrataSensor():
    global CONSOLE
    global SENSORES
    global SOCKETUDP

    while True:
        data, addr = SOCKETUDP.recvfrom(100)
        strdata = data.decode()

        try:
            (comando, dado) = strdata.split(' ', 1)
        except:
            print('\r\nComando invalido do sensor', addr)
            continue

        if comando == 'REGISTRO':
            SENSORES[dado] = addr
            SOCKETUDP.sendto('ACKregistro'.encode(), addr)
            print('O sensor ' + dado + ' registrou')

        elif comando == 'ESTADO':
            if addr not in SENSORES.values():
                ID = 'DESCONHECIDO'
            else:
                for ID, a in SENSORES.items():
                    if a == addr:
                        break
            print('\r\nSensor ' + ID + ' enviou ' + dado + '\r\n')
            if CONSOLE:
                CONSOLE.send('Sensor {} enviou {}\r\n'.format(ID, dado).encode())
