class RFC {
	
	public int rfcNum;
	public String rfcTitle;
	public String hostName;
	public int clientPort; 
	public int connPort;

    //Constructor
	public RFC(int rfcNum, String rfcTitle, String hostName, int clientPort, int connPort) {
		this.rfcNum = rfcNum;
		this.rfcTitle = rfcTitle;
		this.hostName = hostName;
		this.clientPort = clientPort;
		this.connPort = connPort;
	}

    //Getters
    public int getRFCNum() {
		return this.rfcNum;
	}

    public int getRFCTitle() {
		return this.rfcTitle;
	}

	public String getHostName() {
		return this.hostName;
	}

	public int getClientPort() {
		return this.clientPort;
	}

    public int getConnPort() {
		return this.connPort;
	}
	
    //Setters
	public void setRFCNum(int rfcNum) {
		this.rfcNum = rfcNum;
	}

    public void setRFCTitle(int rfcTitle) {
		this.rfcTitle = rfcTitle;
	}

	public void setHostName(String hostName) {
		this.hostName = hostName;
	}

	public void setPortNumber(int clientPort) {
		this.clientPort = clientPort;
	}

    public void setPortNumber(int clientPort) {
		this.connPort = connPort;
	}
}