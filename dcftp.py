import socket
import sys
import time
import os
HOST = '127.0.0.1'          # IP
PORT = 9999                 #Porta

def Download(path, conn):


    file = os.path.basename(path)

    f = open(file, 'wb')
    while True:
    # receive 1000 bytes
        data = conn.recv(1000)
        print("data: ", len(data))
        if len(data) == 0 or data is None:
            break
        else:

            f.write(data)

    f.close()
    return None
def selPastaLocal():

    print('Diretório atual:', os.getcwd())
    print('Conteúdo da pasta:', os.listdir())

    dir = input('Escolha a pasta de Download ou <ENTER> para manter a atual: ')
    if len(dir) > 0:
        try:

            if not os.path.isdir(dir):
                os.makedirs(dir)
            os.chdir(dir)
            print('Pasta Download:', os.getcwd())
        except:
            print('Pasta Download:', os.getcwd())
  
def arquivoRemoto(s):
    s.send(bytes('os.listdir()\n', 'utf-8'))
    time.sleep(2) 
    resposta = s.recv(2048).decode()
    print('Conteúdo remoto: ', resposta)

    dir = input('Digite a pasta de Upload (Remota) ou <ENTER> para manter a mesma:')
    
    if len(dir) > 0:
        if dir not in eval(resposta):
            print('Esse diretorio não pode ser selecionado')
        else: selecionado
            s.send(f'os.listdir({dir})\n'.encode())
            time.sleep(2) 
            resposta = s.recv(2048).decode()
            print('Conteúdo remoto: ', resposta)

    file = input('selecione o arquivo para download: ')
    if file not in eval(resposta):
        print('esse arquivo nao existe')

        file = eval(resposta)[0]

    return os.path.join(dir,file)

    pydir=  os.path.dirname(os.path.realpath(__file__))
    print('Diretorio do script: ', pydir)
    os.chdir(pydir)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except:
        print('# erro de conexao')
        sys.exit()
    print('selecao da pasta local ...')
    selPastaLocal()
    print('selecao do arquivo remoto ...')
    remoto = arquivoRemoto(s)
    if not remoto:
        print('O arquivo remoto não foi selecionado.')
        sys.exit()
    print(remoto)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s2.bind(('', 9998))
        s2.listen(1)
    except:
        print('# erro de bind')
        sys.exit()

    s.send('download({})\n'.format(remoto).encode())
    conn, addr = s2.accept()
    print('Servidor {} fez a conexao'.format(addr))

    Download(remoto, conn)
    conn.close()
    s2.close()
    print('O arquivo foi transferido')
    input('Digite <ENTER> para encerrar')
    s.close()