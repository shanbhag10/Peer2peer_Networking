import java.io.*;

class Peer {

	public int id;
	public String hostName;
	public int portNumber; 
	ObjectInputStream input;
	ObjectOutputStream output;

	public Peer(int id, String hostName, int portNumber, ObjectInputStream input, ObjectOutputStream output) {
		this.id = id;
		this.hostName = hostName;
		this.portNumber = portNumber;
		this.input = input;
		this.output = output;
	}

	public int getID() {
		return id;
	}

	public String getHostName() {
		return hostName;
	}

	public int getPortNumber() {
		return portNumber;
	}
	
    public ObjectInputStream getInput() {
        return input;
    }

    public ObjectInputStream getOutput() {
        return output;
    }

	public void setID(int id) {
		this.id = id;
	}

	public void setHostName(String hostName) {
		this.hostName = hostName;
	}

	public void setPortNumber(int portNumber) {
		this.portNumber = portNumber;
	}

    public void setInput(ObjectInputStream input) {
        this.input = input;
    }

    public void setOutput(ObjectInputStream output) {
        this.output = output;
    }

}