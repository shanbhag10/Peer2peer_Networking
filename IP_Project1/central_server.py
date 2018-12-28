import sys
import socket
import threading
import os
import shlex

class RFC:
    def __init__(self, rfc_number=-1, rfc_title='None',peer_host_name='None', peer_upload_port=-1):
        self.rfc_number=rfc_number
        self.rfc_title=rfc_title
        self.peer_upload_port=peer_upload_port
        self.peer_host_name=peer_host_name

    def __str__(self):
        return str(self.rfc_number)+" "+str(self.rfc_title)+" "+str(self.peer_host_name)+" "+str(self.peer_upload_port)


class Peer:
    def __init__(self,peer_host_name='None',peerPortNo=10000):
        self.peer_host_name=peer_host_name
        self.peerPortNo=peerPortNo

    def __str__(self):
        return str(self.peer_host_name)+' '+str(self.peerPortNo)



def listAll():
    global status, phrase
    status=0
    phrase=''
    temp=[]
    if not rfc_index_list:
        status=404
        phrase='BAD REQUEST'
    else:
        for record in rfc_index_list:
            temp.append(RFC(record.rfc_number,record.rfc_title,record.peer_host_name,record.peer_upload_port))
            status=200
            phrase='OK'
    return temp,status,phrase


def lookup(rfc_number):
    temp=[]
    flag=0

    for record in rfc_index_list:
        print record.rfc_number+" "+rfc_number
        if record.rfc_number==rfc_number:
            temp.append(RFC(record.rfc_number,record.rfc_title,record.peer_host_name,record.peer_upload_port))
            code=200
            phrase='OK'
            flag = 1
    
    if(flag==0):
        code=404
        phrase='FILE NOT FOUND'
    return temp,code,phrase
    

def initialize_peer(data):
    request=shlex.split(data)
    rfc_list=str(data).rsplit(':',1)
    c=shlex.split(rfc_list[1])
    peers.insert(0,Peer(request[3],request[5]))
    for i,j in zip(c[::2],c[1::2]):
        rfc_index_list.insert(0,RFC(i,j,request[3],request[5]))


def managePeer(client_socket,client_address):
    data = client_socket.recv(1024)

    print "\nRequest received from Client :"
    print data

    request=shlex.split(data)
    print request
    if request[0] == 'INITIALIZE':
        index=initialize_peer(data)
        reply="Peer Added"
        client_socket.send(reply)

    elif request[0] == 'LIST':
        reply,code,phrase=listAll()
        response="P2P-CI/1.0 "+str(code)+" "+str(phrase)+"\n"
        for i in reply:
            reply_list=shlex.split(str(i))
            response=response+str(reply_list[0])+" "+reply_list[1]+" "+reply_list[2]+" "+str(reply_list[3])+"\n"
        client_socket.send(response)

    elif request[0] == 'LOOKUP':
        reply,code,phrase=lookup(request[1])
        response="P2P-CI/1.0 "+str(code)+" "+str(phrase)+"\n"
        for i in reply:
            reply_list=shlex.split(str(i))
            response=response+str(reply_list[0])+" "+reply_list[1]+" "+reply_list[2]+" "+str(reply_list[3])+"\n"
        client_socket.send(response)
        
    elif request[0] == 'ADD':
        rfc_index_list.insert(0,RFC(request[1],request[8],request[4],request[6]))
        for record in rfc_index_list:
            code=200
            phrase='OK'
        title=data.splitlines()[3].split(":")
        response="P2P-CI/1.0 "+str(code)+" "+str(phrase)+"\n"
        response=response+"RFC "+request[1]+" "+title[1]+" "+request[4]+" "+request[6]
        client_socket.send(response)


peers=[]
rfcs=[]
rfc_index_list=[]    

server_hostname = socket.gethostname()
print "Host Name: ",server_hostname
server_port = int(sys.argv[1])
print "Port: ",server_port
serversocket = socket.socket()
server_IP_Address = socket.gethostbyname(server_hostname)
print "IP : ",server_IP_Address
serversocket.bind((server_IP_Address,server_port))
serversocket.listen(5)
print "Server has started successfully"

while(True):
    client_socket, client_address = serversocket.accept()
    server_thread = threading.Thread(target=managePeer, args=(client_socket,client_address))
    server_thread.start()

serversocket.close()

    
