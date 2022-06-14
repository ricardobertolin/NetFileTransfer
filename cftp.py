import ast
import socket
import sys
import time
import os

HOST = '127.0.0.1'          # IP
PORT = 9999                 #Port
diretorio = 'OFFBOUNDS'

def Upload(file, conn):

    with open(file,'r') as f:

        for line in f:

enconde())
            conn.send(line.encode())

pydir=  os.path.dirname(os.path.realpath(__file__))
print('Diretorio do script: ', pydir)
os.chdir(pydir)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST, PORT))
except:
    print('# erro de conexao')
    sys.exit()
diretórios)
s.send(bytes('os.listdir()\n', 'utf-8'))
time.sleep(2)
while
resposta = s.recv(2048).decode()

if diretorio not in resposta:
    print('Diretorio nao encontrado')

    s.send(bytes('os.makedirs({})\n'.format(diretorio),'utf-8'))
    time.sleep(2)
    print(s.recv(2048).decode())
else:
    print('Conteudo do diretorio:')
    


    s.send(bytes('os.listdir({})\n'.format(diretorio), 'utf-8'))
    time.sleep(2)
    resposta = s.recv(2048).decode()
    #print(type(resposta))
    resposta = ast.literal_eval(resposta)
    print(type(resposta))

print(os.getcwd())
print(os.listdir())
while True:
    arquivo = input('Digite o nome do arquivo para transferir: ')
    arquivo2 = os.path.join ('CLIENTE',arquivo)
    if not arquivo:
        print('<ENTER> encerra o programa')
        sys.exit()
    elif arquivo in resposta:
        print ('Este arquivo ja esxiste no servidor')
    elif not os.path.isfile(arquivo):
        print('este arquivo nao existe no client')
    else:
        print('OK')
        break

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s2.bind(('', 9998))
    s2.listen(1)
except:
    print('# erro de bind')
    sys.exit()

s.send(bytes('upload({}\\{})\n'.format(diretorio,arquivo), 'utf-8'))

conn, addr = s2.accept()
print('Servidor {} fez a conexao'.format(addr))

Upload(arquivo, conn)
conn.close()
s2.close()
print('O arquivo foi transferido')
input('Digite <ENTER> para encerrar')