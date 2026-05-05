# server.py
import socket
import threading

# host = '74:13:ea:f9:60:3b'
# port = 4
# server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

host = '127.0.0.1'
port = 5555
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(mess):
    for client in clients:
        client.send(mess)

def handle(client):
    while True:
        try:
            mess = client.recv(1024)
            broadcast(mess)
        except:
            idx = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[idx]
            broadcast(f'{nickname} left the chat!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, addr = server.accept()
        print(f'Connected with {str(addr)}')

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        clients.append(client)
        nicknames.append(nickname)

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
        client.send('Connected to the server!'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print('Server is listening...')
receive()