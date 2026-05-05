# client.py
import socket
import threading

# host = '74:13:ea:f9:60:3b'
# port = 4
# client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

host = '127.0.0.1'
port = 5555
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

nickname = input('Choose a nickname: ')

client.connect((host, port))

def receive():
    while True:
        try:
            mess = client.recv(1024).decode('utf-8')
            if mess == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                print(mess)
        except:
            print('An error occurred!')
            client.close()
            break

def write():
    while True:
        mess = f'{nickname}: {input()}'
        client.send(mess.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()