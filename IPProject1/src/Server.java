import java.util.*;
import java.io.*;
import java.net.*;

public class Server {

	// Configuration Details
	public static final int SERVER_PORT = 7734; // Well-known port number
	public static String operatingSystem = System.getProperty("os.name");
	public static final String VERSION = "P2P-CI/1.0";

	private ServerSocket serverSocket;
	private List<Peer> peers;
	private List<RFC> rfcs; 
	private int peerCount;

	public static void main(String args[]) throws Exception {
		Server server = new Server();
	}

	// Constructor
	public Server() {
		this.peers = Collections.synchronizedList(new ArrayList<Peer>());
		this.rfcs = Collections.synchronizedList(new ArrayList<RFC>());
		this.peerCount = 0;

		try {
			this.serverSocket = new ServerSocket(SERVER_PORT, 100);
			System.out.println();
			System.out.println("Server started successfully.");
			System.out.println("Host: " + InetAddress.getLocalHost().getHostAddress()); 
			System.out.println("Port Number: " + SERVER_PORT);
			System.out.println("Version: " + VERSION);
			System.out.println("Operating System: " + operatingSystem);
			this.serverListen();
		}
		catch(Exception e) {
			System.out.println("Error occurred while starting server.");
			e.printStackTrace();
		}
	}

	private void serverListen() {
		while(true) {
			try {
				Socket connectionSocket = serverSocket.accept();
				Peer peer = connectPeer(connectionSocket);
				Thread peerThread = new Thread(new Runnable() {
					public void run() {
						handlePeer(peer);
					}
				});
				peerThread.start();
			}
			catch(Exception e) {
				System.out.println("Error establishing connection with new client.");
				e.printStackTrace();
			}
		}

	}

	private Peer connectPeer(Socket connectionSocket) throws Exception {

		// Creating a new peer object
		int peerPort = connectionSocket.getPort();
		InetAddress peerInetAddr = connectionSocket.getInetAddress();
		String peerHostName = peerInetAddr.getHostName();
		this.peerCount++;
		int peerId = this.peerCount;
		ObjectOutputStream output = new ObjectOutputStream(connectionSocket.getOutputStream());
		ObjectInputStream input = new ObjectInputStream(connectionSocket.getInputStream());
		Peer peer = new Peer(peerId, peerHostName, peerPort, input, output);

		peers.add(peer);
		System.out.println();
		System.out.println("Peer " + peerId + " connected.");
		System.out.println("Host Name: " + peerHostName);
		System.out.println("Port Number: " + peerPort);

		return peer;

	}

	private void handlePeer(Peer peer) {
		try {
			while(true) {
				System.out.println();
				String peerRequest = (String) peer.getInput().readObject();
				System.out.println("INCOMING REQUEST: ");
				System.out.println(peerRequest);
				String[] method = peerRequest.trim().split("\\s");
				handleRequest(peer, method[0].trim());
			}
		}
		catch(Exception e) {
			closeConnection(peer);
			return;
		}
	}

	private void handleRequest(Peer peer, String method) {
		try {
			if("LIST".equals(method)) {
				listAllRFCs(peer);
			}
			else if("ADD".equals(method)) {
				addRFC(peer);
			}
			else if("LOOKUP".equals(method)) {
				lookupRFC(peer);
			}
		}
		catch(Exception e) {
			e.printStackTrace();
		}
	}

	public void printAllPeers() {
		System.out.println();
		System.out.println("List of Peers:");
		for(Peer p : peers) {
			System.out.println("\t" + "Peer " + p.getId() + ": " + p.getHostName() + " : " + p.getPortNumber());
		}
	}

	// Lookup RFC
	private void lookupRFC(Peer peer) throws Exception {
		ObjectOutputStream output = peer.getOutput();
		try {
			ObjectInputStream input = peer.getInput();
			int rfcNumber = Integer.parseInt((String) input.readObject());
			String rfcTitle = (String) input.readObject();

			List<RFC> matchingRecords = new ArrayList<>(); 

			for(RFC record : rfcs) {
				if(record.getRFCNumber() == rfcNumber && record.getRFCTitle().equals(rfcTitle)) {
					matchingRecords.add(record);
				}
			}

			if(matchingRecords.isEmpty()) {
				output.writeObject("404 Not Found");
			}
			else {
				output.writeObject("\n\n" + VERSION + " 200 OK");
				for(RFC record : matchingRecords) {
					output.writeObject("RFC " + record.getRFCNumber() + " " + record.getRFCTitle() + " " + record.getHostName() + " " + record.getClientPort() + "\n");

				}
				output.writeObject("\n");
			}
		}
		catch (Exception e) {
			output.writeObject("\n" + VERSION + " 400 Bad Request");
			e.printStackTrace();
		}
	}

	// List all RFCs
	private void listAllRFCs(Peer peer) {
		try {
			ObjectInputStream input = peer.getInput();
			ObjectOutputStream output = peer.getOutput();
			output.writeObject(VERSION + " 200 OK\n");

			for(RFC record : rfcs) {
				output.writeObject("RFC " + record.getRFCNumber() + " " + record.getRFCTitle() + " " + record.getHostName() + " " + record.getClientPort() + "\n");
			}
			output.writeObject("\n");
		}
		catch(Exception e){
			e.printStackTrace();
		}
	}
		
	// Method to add RFC
	private void addRFC(Peer peer) throws Exception {
		try {
			ObjectInputStream input = peer.input;
			ObjectOutputStream output = peer.output;
			int rfcNumber = Integer.parseInt((String) input.readObject());
			String rfcTitle = (String) input.readObject();
			String hostName = (String) input.readObject();
			int portNumber = Integer.parseInt((String) input.readObject());
			int connPort = Integer.parseInt((String) input.readObject());
			
			RFC rfc = new RFC(rfcNumber, rfcTitle, hostName, portNumber, connPort);
			rfcs.add(rfc);
			System.out.println("RFC " + rfcNumber + " added successfully.");
			output.writeObject("RFC " + rfcNumber + " added successfully.");
		}
		catch (Exception e) {
			System.out.println(e);
		}
	}

	private void closeConnection(Peer peer) {
		System.out.println("in closeConnection");

		removePeer(peer);
		removerfcs(peer.hostName, peer.portNumber);
		System.out.println();
		System.out.println("Connection with peer " + peer.id + " closed.");
	}

	// Method to remove peer from peer list
	private void removePeer(Peer peer) {
		this.peers.remove(peer);
	}

	// Method to remove RFC records of a peer
	private void removerfcs(String hostName, int portNumber) {
		try {

			for (Iterator<RFC> iterator = this.rfcs.iterator(); iterator.hasNext();) {
			    RFC record = iterator.next();
			    System.out.println("Checking : peer port = " + record.connPort);
			    if (portNumber == record.connPort) {
			        // Remove the current element from the iterator and the list.
			        iterator.remove();
			    }
			}

		}
		catch(Exception e) {
			e.printStackTrace();
		}
	}

}