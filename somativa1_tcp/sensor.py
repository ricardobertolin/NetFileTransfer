import socket
import sys

ESTADO = 'OFF'

def interpretaComando(comando, s):
    global ESTADO
    print('Recebi o comando', comando)
    if comando.lower() == 'ligar':
        ESTADO = 'ON'
    elif comando.lower() == 'desligar':
        ESTADO = 'OFF'
    elif comando.lower() == 'consulta':
        s.send(ESTADO.encode())
    else:
        print('comando desconhecido: ', comando)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = input('IP do monitor: ')
PORTA = int(input('Porta do monitor: '))
ID = input('ID do sensor: ')

try:
    s.connect((IP, PORTA))
    s.send(ID.encode())
except:
    print('erro de conexao')

while True:
    try:
        dados = s.recv(100).decode()
        interpretaComando(dados, s)
    except:
        print('Erro na conexão com o monitor')
        sys.exit()
