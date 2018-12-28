



Peer to Peer system with Centralized Index.

Running Instructions:

1. Server :
python central_server.py <server port>

Example: python central_server.py 7734 will start the server on port no. 7734.


2. Client (peer) :
Go to the folder with your RFCs and copy the peer code. For ease of testing, we haven't added absolute paths.

We have provided two mock folders with txt files as RFCs. To test with the same, please start clients inside these folders.

cd C1_MockRFCs 
python peer.py <upload port>

Example: python peer.py 6666 will give this peer the upload port 6666.