import java.util.*;
import java.io.*;
import java.net.*;
import java.text.*;
import java.sql.Date;
import java.nio.file.Files;

public class Client implements Runnable {

	public static final String VERSION = "P2P-CI/1.0";

	private ServerSocket serverSocket;
	private static String RFCPath;

	private static Socket connectionSocket;
	private static String serverHostName;
	private static String clientHostName;
	private static int clientUploadPort;
	private static int connectionPort;
	private static ObjectOutputStream output;
	private static ObjectInputStream input;
	private static BufferedReader br = null;
	private static Map<String, String> errorMap = null;

	public static void main(String args[]) throws Exception {
		try {

			errorMap = intializeErrorMap();

			// Get server information
			System.out.println("\nEnter Server IP Address: ");
			String serverIpAddr = System.console().readLine();
			serverHostName = InetAddress.getByName(serverIpAddr).getHostName();
			
			Random rand = new Random();
			int randomNumber = rand.nextInt(1000);
			int clientListenPort = randomNumber + 6000; // To avoid port number in well-defined ports
			new Client(clientListenPort);

			// Connecting to server
			connectionSocket = new Socket(serverIpAddr, Server.SERVER_PORT);
			output = new ObjectOutputStream(connectionSocket.getOutputStream());
			input = new ObjectInputStream(connectionSocket.getInputStream());
			connectionPort = connectionSocket.getLocalPort();
			System.out.println();
			System.out.println("Client connected to server successfully.");
			System.out.println("Host Name: " + serverHostName);
			System.out.println("Port Number: " + connectionPort + "\n\n");

			// Get RFC directory path
			System.out.print("Enter RFC directory path: ");
			RFCPath = System.console().readLine().trim();

			br = new BufferedReader(new InputStreamReader(System.in));
			while(true) {
				if(br != null) {
					// Display menu
					System.out.println("\nOPTIONS:");
					System.out.println("\t" + "1. List all RFCs");
					System.out.println("\t" + "2. Lookup RFC");
					System.out.println("\t" + "3. Download RFC");
					System.out.println("\t" + "4. Add RFC");
					System.out.println("\t" + "5. Update RFC directory");
					System.out.println("\t" + "6. Exit");
					System.out.println("\nEnter option number: ");

					String option = br.readLine().trim();
					if(!"".equals(option)) {
						int opt;
						try {
							opt = Integer.parseInt(option);
						}
						catch(NumberFormatException e) {
							System.out.println("Enter valid number.");
							continue;
						}
						switch(opt) {
							case 1:
								requestRFCList();
								break;
							case 2:
								requestRFCLookup();
								break;
							case 3:
								p2pFileRequest();
								break;
							case 4:
								requestRFCAdd();
								break;
							case 5:
								changeDirectory();
								break;
							case 6:

								System.exit(1);
								break;
							default:
								System.out.println("\nInvalid option.");
								
						}
					}
				}

			}
		}
		catch(Exception e) {
			System.out.println("Error occurred in client.");
			e.printStackTrace();
		}

	}

	public Client(int portNumber) throws Exception {
		// Upload server of client
		serverSocket = new ServerSocket(portNumber);
		new Thread(this).start();
		System.out.println();
		System.out.println("Client started successfully.");
		String serverSocketIP = InetAddress.getLocalHost().getHostAddress();
		clientUploadPort = serverSocket.getLocalPort();
		clientHostName = InetAddress.getByName(serverSocketIP).getHostName();
		System.out.println("IP Address: " + serverSocketIP);
		System.out.println("Upload Port Number: " + clientUploadPort);
	}

	// Requesting RFC list from server
	private static void requestRFCList() {
		try {
			output.writeObject("LIST ALL " + VERSION + "\nHost: " + clientHostName + "\nPort: " + clientUploadPort + "\n");
			String response = ((String) input.readObject()).trim();
			System.out.println();
			System.out.println(response);
			if (!response.startsWith(VERSION)) {
				System.out.println("Error: Peer has different version");
				return;
			}
			if((response.contains("200 OK"))) {
				response = (String) input.readObject();
				while (response.equalsIgnoreCase("\n") == false) {
					System.out.print(response);
					response = (String) input.readObject();
				}
				return;
			} else{
				System.out.println(getErrorMessage(response));
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	/*

	Method to send request to add RFC to server

	ADD RFC 123 P2P-CI/1.0
	Host: thishost.csc.ncsu.edu
	Port: 5678
	Title: A Proferred Official ICP

	*/
	private static void requestRFCAdd() {

		try {
			System.out.println("Enter RFC Number (Eg: If adding RFC123.txt, enter 123): ");
			String rfcNumber = br.readLine();
			System.out.println("Enter RFC Title: ");
			String rfcTitle = br.readLine();
			if(rfcNumber == null || rfcTitle == null || "".equals(rfcNumber) || "".equals(rfcTitle)) {
				System.out.println("Invalid RFC details.");
				return;
			}
			String rfcFile = "RFC" + rfcNumber.trim() + ".txt";
			String tempFile = RFCPath + "/" + rfcFile;

			File file = new File(tempFile);
			boolean fileExists = file.exists();

			if(fileExists) {
				output.writeObject("ADD RFC " + rfcNumber + " " + VERSION + "\nHost:"+ clientHostName + "\nPort:" + clientUploadPort + "\nTitle:" + rfcTitle + "\n");
				output.writeObject(String.valueOf(rfcNumber));
				output.writeObject(rfcTitle);
				output.writeObject(clientHostName);
				output.writeObject(String.valueOf(clientUploadPort));
				output.writeObject(String.valueOf(connectionPort)); 
				System.out.println();
				System.out.println("RESPONSE:");
				System.out.println(input.readObject());
			}
			else {
				System.out.println(tempFile);
				System.out.println("File does not exist. Check file name or your RFC directory path.");
				System.out.println(errorMap.get("404"));
			}
		} catch(Exception e){
			System.out.println("\nError occurred while adding RFC.");
			e.printStackTrace();
		}
	}

	// Method to request RFC lookup to server
	private static void requestRFCLookup() throws IOException {

	try {
		System.out.println("Enter RFC number: ");
		String rfcNumber = br.readLine().trim();
		System.out.println("Enter RFC title:");
		String rfcTitle = br.readLine().trim();
		System.out.println();
		output.writeObject("LOOKUP RFC " + rfcTitle + " " + VERSION + "\nHost: " + clientHostName + "\nPort: " + clientUploadPort + "\nTitle: " + rfcTitle + "\n");
		output.writeObject(rfcNumber);
		output.writeObject(rfcTitle);
		String resp = ((String) input.readObject()).trim();
		System.out.println(resp);
		if ((resp.contains("200 OK"))) {
			resp = (String) input.readObject();
			while (resp.equalsIgnoreCase("\n") == false) {
				System.out.print(resp);
				resp = (String) input.readObject();
			}
			return;
		} else{
			System.out.println("\nError occurred while looking up RFC.");
			System.out.println(getErrorMessage(resp));
		}
	}
	catch (Exception e) {
			e.printStackTrace();
		}
	}

	// Method to request file from peer
	private static void p2pFileRequest() {
		try {
			// Getting RFC & peer details from user
			System.out.println("Enter RFC number: ");
			String rfcNumber = br.readLine().trim();
			System.out.println("Enter RFC title: ");
			String rfcTitle = br.readLine().trim();
			System.out.println("Enter peer host name: ");
			String peerHostName = br.readLine().trim();
			System.out.println("Enter peer port number: ");
			int peerPort = Integer.parseInt(br.readLine().trim());

			// Connecting with peer
			Socket downloadSocket = new Socket(peerHostName, peerPort);
			System.out.println("Connected with peer.");

			ObjectOutputStream sockOutput = new ObjectOutputStream(downloadSocket.getOutputStream());
			ObjectInputStream sockInput = new ObjectInputStream(downloadSocket.getInputStream());
			String operatingSystem = System.getProperty("os.name");

			// Sending GET request
			sockOutput.writeObject("GET RFC " + rfcNumber + " " + VERSION + "\nHost: "+ peerHostName + "\nOS: " + operatingSystem + "\n");
			sockOutput.writeObject(rfcNumber);
			
			// Getting response from peer
			String peerResponse = ((String) sockInput.readObject()).trim();
			System.out.println(peerResponse);
			if(!peerResponse.startsWith(VERSION)) {
				System.out.println(errorMap.get("505"));
				return;
			}
			if((peerResponse.contains("200 OK"))) {
				File downloadFile = new File(RFCPath + "\\RFC" + rfcNumber + "_2.txt");
				downloadFile.createNewFile();
				try {
					byte[] content = (byte[]) sockInput.readObject();
					Files.write(downloadFile.toPath(), content);
				} 
				catch (EOFException eof) {
					System.out.println("End of file");
				}
			}
			else {
				System.out.println(getErrorMessage(peerResponse));
			}
		} catch (Exception e) {
			System.out.println("Error in peer-to-peer RFC download.");
		}
	}

	// Writing file to peer
	private void writeFileAtPeer(ObjectInputStream sockInput, ObjectOutputStream sockOutput) throws Exception {
		String rfcNumber = (String) sockInput.readObject();
		String downloadFileName = "RFC" + rfcNumber + ".txt";          
		File file = new File(RFCPath + "\\" + downloadFileName);
		
		boolean fileExists = file.exists();
		if(fileExists) {
			String response = VERSION + " 200 OK\n";
			response += "Date: " + (new SimpleDateFormat("EEE, d MMM yyyy HH:mm:ss")).format(new Date(0)) + " GMT\n";
			response += "OS: " + System.getProperty("os.name") + "\n";
			response += "Last Modified: " + (new SimpleDateFormat("EEE, d MMM yyyy HH:mm:ss")).format(new Date(file.lastModified())) +" GMT\n";
			response += "Content-Length: " + file.length() + "\n";
			response += "Content-Type: text/text\n";

			sockOutput.writeObject(response);
			byte[] data = Files.readAllBytes(file.toPath());
			sockOutput.writeObject(data);
		}
		else {
			sockOutput.writeObject(VERSION + " 404 Not Found\n");
			sockOutput.flush();
		}
		sockOutput.close();
	}

	@Override
	public void run() {
		try {
			Socket uploadSocket = serverSocket.accept();
			new Thread(this).start(); 
			ObjectInputStream inputStream = new ObjectInputStream(uploadSocket.getInputStream());
			ObjectOutputStream outputStream = new ObjectOutputStream(uploadSocket.getOutputStream());
			
			String response = (String) inputStream.readObject();
			System.out.println(response);
			if (response.contains("GET")) {
				writeFileAtPeer(inputStream, outputStream);            
			}

			outputStream.close();
			inputStream.close();
			uploadSocket.close();

		}
		catch (Exception e) {
			System.out.println("Error in peer-to-peer download.");
		}
	}

	private static void changeDirectory() {
		System.out.print("\nEnter RFC directory path: ");
		RFCPath = System.console().readLine().trim();
		System.out.println("RFC directory path updated successfully.\n");
	}

	// Initializing map of error codes & messages
	public static Map<String, String> intializeErrorMap() {
		Map<String, String> errorMap = new HashMap<>();
		errorMap.put("400", "400 Bad Request");
		errorMap.put("505", "505 P2P-CI Version Not Supported");
		errorMap.put("404", "404 Not Found");
		return errorMap;
	}

	public static String getErrorMessage(String response) {
		for(String errorCode : errorMap.keySet()) {
			if(response.contains(errorCode)) {
				return errorMap.get(errorCode);
			}
		}
		return "Error occurred.";
	}

}