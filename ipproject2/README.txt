NOTE: Make sure that you are running the programs with Python 2.x and not Python 3.x

Steps to run the code -

1. Run the simple_ftp_server code from the terminal by typing -
python simple_ftp_server.py server-port recv-file-name packet-loss-probability

2. From the client machine (The one which will send the data), first navigate to the directory where the
simple_ftp_client.py file is. Make sure that the simple_ftp_client.py file and the send_data.txt file are in the same
directory. Then from the terminal, run the following command -
python2 simple_ftp_client.py server-IP server-port-no send-file-name N-value MSS-value

3. After these steps are done, you will see that there is a file created in the directory of the server code with the
name provided in the command - recv-file-name.txt

cd Desktop/CSC\ 573\ Internet\ Protocols/Project\ 2
python2 simple_ftp_server.py 7735 recv_file.txt 0.01
python2 simple_ftp_client.py 192.168.1.9 7735 send_data.txt 500 500