import os
import time
from threading import Thread
import socket

clients_Address = {} #dictioanry storing client's ip address and maps ip->client name(or UID)
clients_Name = {}    #ditionary storing client's name(or UID) and maps UID->client's ip
file_port = {33333:0}  #dictionary storing available file ports for sending files maps port no->port's status



IP = input('Enter the IP address')
PORT = int(input('Enter the port no. '))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #TCP/Ip Socket
server.bind((IP,PORT))  #binds to local host(or given IP address) and port no.
server.listen(5)   #listens for atmost n no. of clients



def file_send(fileName, sender, reciever):
    """
    This function is invoked whenever a file transaction has to be commit i.e., file to be transferred.
    This is involed on a new Thread and it creates a new socket with available port no. if a port is busy then next port is used.
    Firstly it creates a new socket connection with the sender and then recieves the file and then closes the connection.
    Then, it creates another connection with reciever and then sends the file.

    :param fileName:
    :param sender:
    :param reciever:
    :return:
    """
    print('Senfddddd........')
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.bind((IP ,33333))
    new_socket.listen()

    print('File Server Started...')

    t_socket,addr = new_socket.accept()
    t_socket.send('Connected..'.encode())
    print('connected to File',t_socket)


    print(f'sending {fileName} from {sender} to {reciever}')

    if fileName in os.listdir():
        fileName = f'{sender}' + fileName

    file = open(fileName,'wb')
    run = True
    while run:
        line = t_socket.recv(1024)
        if '$$QUIT'.encode() in line:
            run = False
        else:
            file.write(line)
    file.close()
    print('File recieved.....')
    t_socket.close()


    reciever.send(f'$$(file) {file_port} {fileName} '.encode())

    t_socket, addr = new_socket.accept()
    print('Sending File......')
    file = open(fileName, 'rb')
    
    for line in file:
        t_socket.send(line)
    
    t_socket.send('$$QUIT'.encode())
    t_socket.close()
    print('File Sent...')
    
    new_socket.close()
    


    """
        SOCKET = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        r_sock = reciever.getsockname()
        r_sock = r_sock[0]
        print(r_sock)
        SOCKET.connect((r_sock,33343))
        print('Connected for recv....')
    
        file = open(fileName,'rb')
        for line in file:
            SOCKET.send(line)
        print('Sentttt file...')
        file.close()
    """


def recv(x):
    """
    This method is invoked for each client connected to the server and is run on a seperate thread for each client.
    :param x: x is the client socket object
    :return: return None/nothing
    """
    run = True
    while run:
        """ This thread runs until the client doesn't send quit."""
        try:
            msg = x.recv(1024)
            if msg:  #if msg has some content
                msg = msg.decode()  #decode the message
                print(msg,' from ',clients_Address[x])
                if '$$Quit' in msg:   #if $$Quit in msg -> close this thread and close the connection
                    run = False
                if '$(' in msg:       #if $( in msg :-> peer - to - peer msessage
                    peer = msg.split()  #To seperate reciever's name
                    peer = peer[0][2:-1]  #reciever's name
                    #print(f'reciever : {peer} address : {clients_Name[peer]}')
                    peer = clients_Name[peer]   #gets reciever's addresss
                    peer.send(msg.encode())      # sends message

                elif '$$file(' in msg:    #if $$file in mesg-> then peer-to peer file transfer is to be done on seperate thread
                    peer = msg.split()    #To extract file info , peer name
                    file = peer[1]         #File name
                    peer = peer[0][7:-1]    #Reciever's name
                    #Start thread on function = file_send
                    t = Thread(target=file_send,args=(file, clients_Address[x],clients_Name[peer]))
                    t.start()

                else:
                    print("Broadcasting ...")
                    msg = msg.encode()
                    try:
                        for client in clients_Address:
                            print(f'Sent to {clients_Address[client]}')
                            client.send(msg)
                    except:
                        pass

            time.sleep(1/30)

        except:
            pass
    clients_Name.pop(clients_Address[x])
    clients_Address.pop(x)
    x.close()


def start():
    while True:
        c, addr = server.accept()
        #print('got connection from ',c)
        info = c.recv(100)
        info = info.decode()
        print(info,' connected...')
        try:
            if clients_Name[info] in clients_Address:
                print(clients_Address.pop(clients_Name[info]))
        except:
            pass

        clients_Address[c] = info
        print(clients_Address)
        clients_Name[info] = c
        t1 = Thread(target=recv, args=(c,))
        t1.start()



start()
