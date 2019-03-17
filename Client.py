import os
import time
from threading import Thread
import socket

info = input('Enter the name')
file_port = 33333

IP = input('Enter the IP address')
PORT = int(input('Enter the port no. '))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP, PORT))
client.send(info.encode())
client.setblocking(0)

file_port_recv =None

def recv():
    while True:
        try:
            msg = client.recv(1024)
            if msg:
                msg = msg.decode()
                print(msg)
                if '$$(file)' in msg:
                    file_port_recv = msg.split()
                    fileName = file_port_recv[2]
                    file_port_recv = file_port_recv[1]
                    t = Thread(target= recvFile, args=(fileName, file_port_recv))
                    t.start()


            time.sleep(1/30)
        except:
            pass


def recvFile(fileName, port):
    sock = connectFileSocket()
    if sock:
        print('Recieving file........')

        if fileName in os.listdir():
            fileName = 'New_'+fileName
        file = open(fileName,'wb')
        run = True

        while run:
            line = sock.recv(1024)
            if '$$QUIT'.encode() in line:
                run = False
            else:
                file.write(line)
        file.close()
        print('File recieved.....')
        sock.close()



def connectFileSocket():
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    run = True
    while run:
        try:
            new_socket.connect((IP, file_port))

            m = new_socket.recv(100)
            if m:
                print('File Connected')
                run = False
                return new_socket
            time.sleep(1 / 30)
        except:
            pass
            return None

def sendFile(filePath, reciever):
    print('To sendddd.....')
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    run = True
    while run:
        #print('Trying....')
        try:
            new_socket.connect((IP, file_port))
            m = new_socket.recv(1024)
            if m:
                print('File Connected')
                run = False
        except:
            pass

    print('Exitingggg...')

    file = open(filePath,'rb')
    for line in file:
        new_socket.send(line)
        time.sleep(1/30)
    file.close()
    new_socket.send('$$QUIT'.encode())
    print('File sent')
    new_socket.close()








def menu():
    print('For Peer-to-Peer : Type $(Reciever\'s name) then start typing the message')
    print('For generic or broadcast message , simply type the message and send')
    print('For sending a file Type $$file(Reciever\'s name) then type filename')

def start():
    menu()
    run = True
    while run:
        try:
            msg = input()
            if '$$Quit' in msg:
                run = False

            elif '$$file(' in msg:
                fileName = msg.split()
                reciever = fileName[0][7:-1]
                fileName = fileName[1]
                t = Thread(target= sendFile, args= (fileName, reciever))
                t.start()
            client.send(msg.encode())
        except Exception as e:
            print('Message cannot be send error :',e)
            break

    client.close()


t1 = Thread(target= recv)
t1.start()

start()