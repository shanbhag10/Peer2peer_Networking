import sys
import socket
import threading
import os
import shlex



def listRFC(serverIP,serverPort):
    message="LIST P2P-CI/1.0\nHost: "+client_IP+"\nPort: "+str(client_port)
    client(message,serverIP,serverPort)
    return

def lookupRFC(serverIP,serverPort):
    print "Enter RFC number"
    rfc_number = int(raw_input())
    message="LOOKUP"+" "+str(rfc_number)+" P2P-CI/1.0\n Host: "+client_IP+"\n Port: "+str(client_port)
    client(message,serverIP,serverPort)
    return

def addRFC(serverIP,serverPort):
    print "Enter RFC number"
    rfc_number=raw_input()
    print "Enter RFC title"
    rfc_title=raw_input()
    records.insert(0,str(rfc_number)+"-"+rfc_title)
    message="ADD "+rfc_number+" P2P-CI/1.0\nHost: "+client_IP+"\n Port: "+str(client_port)+"\n Title: "+rfc_title
    client(message,serverIP,serverPort)
    print("RFC Added Successfully")
    return


def download(message,rfc_number,peer_name,peer_port,file_name):

    client_socket=socket.socket()
    peer_ip=peer_name
    client_socket.connect((peer_ip,peer_port))

    print "P2P Connection Successful"
    client_socket.send(message)
    reply=client_socket.recv(1024)
   
    reply_list=shlex.split(reply)
    os.chdir(os.getcwd())
    file_name=file_name+".txt"

    if str(reply_list[1])=='200':
        f=open(file_name,'wb')
        while True:
            nextMsg=client_socket.recv(1024)
            if nextMsg:
                f.write(nextMsg)
                break
            else:
                f.close()
                break
    else:
        print "P2P-CI/1.0 404 FILE NOT FOUND"
    client_socket.close()
    return


def downlaodRFC(name,sock):
    request=sock.recv(1024)
    print request
    rfc_number=shlex.split(request)
    file_found = 0
    for rec in records:
        
        item = rec.split("-")
        
        if int(item[0])==int(rfc_number[2]):
            file_found=1
            file_name=str(rec)+".txt"
    
    if file_found:
        print "File Found"
        file_data="P2P-CI/1.0 200 OK"+"\n"
        sock.send(file_data)
        try:
            with open(file_name,'r') as temp:
                bytesRequiredToSend = temp.read(1024)
                sock.send(bytesRequiredToSend)
            while bytesRequiredToSend != "":
                    bytesRequiredToSend = temp.read(1024)
                    sock.send(bytesRequiredToSend)
        except Exception as error:
            print error
            print "File Transferred"
    else:
        print "File was not found"
        file_data="P2P-CI/1.0 404 FILE NOT FOUND"+"\n"
        sock.send(file_data)
    sock.close()
    return




def getRFC(serverIP,serverPort):
    print "Enter RFC number"
    rfc_number=int(raw_input())
    print "Enter RFC title"
    rfc_title=raw_input()
    print "Enter Peer HostName"
    name_peer=raw_input()
    print "Enter Peer upload port number"
    port_peer=int(raw_input()) 
    message="GET RFC "+str(rfc_number)+" "+rfc_title+" P2P-CI/1.0\nHost: "+name_peer+"\n"
    file_name=str(rfc_number)+"-"+rfc_title
    download(message,rfc_number,name_peer,port_peer,file_name)
    print "File: ",file_name," successfully received"
    return
    

def client(message, serverIP, serverPort):
    print(message)
    c_sock = socket.socket()
    c_sock.connect((serverIP,serverPort))
    c_sock.send(message)
    reply=c_sock.recv(1024)
    print reply
    print 
    c_sock.close()



def main():
    temp_rfc_list=list()
    temp_title_list=list()
    print "Enter Server IP:"
    serverIP=raw_input()
    print "Enter Server Port Number:"
    serverPort=int(raw_input())
    message="INITIALIZE P2P-CI/1.0 Host: "+client_IP+" Port: "+str(client_port)+"\n"
    client(message,serverIP,serverPort)
    
    while(True):
       
        print "CHOOSE OPERATION : "
        print "1. ADD RFC"
        print "2. LOOKUP RFC"
        print "3. LIST RFC"
        print "4. GET RFC FROM PEER"

        choice=int(raw_input())
        
        if choice == 1:
            addRFC(serverIP,serverPort)
        elif choice == 2:
            lookupRFC(serverIP,serverPort)
        elif choice == 3:
            listRFC(serverIP,serverPort)
        elif choice == 4:
            getRFC(serverIP,serverPort)
        else:
            print "Wrong choice"
    return            


def client_server():
    clients_server_socket = socket.socket()
    clients_server_ip=client_IP
    clients_server_port=client_port
    clients_server_socket.bind((clients_server_ip,clients_server_port))
    clients_server_socket.listen(2)

    clients_server_thread = threading.current_thread()
    while(True):
        (peer_socket,peer_addr)=clients_server_socket.accept()
        thread_third=threading.Thread(target=downlaodRFC,args=("dlthread",peer_socket))
        thread_third.start()
        thread_third.join()
    clients_server_socket.close()
    return


client_hostname=socket.gethostname()
client_IP=socket.gethostbyname(client_hostname)
client_port=int(sys.argv[1])

rfc_list=[]
rfc_title=[]
records=[]

try:
    listen_thread = threading.Thread(target=client_server)
    send_thread = threading.Thread(target=main)

    listen_thread.daemon=True
    send_thread.daemon=True

    listen_thread.start()
    send_thread.start()

    listen_thread.join()
    send_thread.join()

except:
    print "Thread Error"