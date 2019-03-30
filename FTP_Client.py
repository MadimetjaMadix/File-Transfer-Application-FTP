import sys
import time
import socket
import threading


def initializeFTPConnection(host_name):
	
	host_port = 21
	host_adr  = (host_name, host_port) 
	
	control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	try:
		control_socket.connect(host_adr)
	except:
		
		print("Failed to connect to ", host_name )
		time.sleep(3)
		return
		
	return control_socket

def login(username = '', password = '')
	
	control_socket = initializeFTPConnection(socket.gethostname())
	
	command  = 'USER ' + username + '\r\n' 
	response = send_command(command)
	
	ErrorCodes = ['530', '500', '501', '421']
	if response[0] not in ErrorCodes
		
		command  = 'PASS ' + password + '\r\n' 
		response = send_command(command)
		
	print('logged in successfuly')

 
def send_command(control_socket, command):
	
	control_socket.send(command.encode())
	response = control_socket.recv(8192).decode()
	responseCode, message = response.split(" ", 1)
	
	return responseCode, message

def dataConnection(bufferSize,control_socket):
	
	#PASV
	command  = 'PASV\r\n' 
	response = send_command(control_socket, command)
	response = response[1]
	firstBracketIndex = response.find("(")
	lastBracketIndex  = response.find(")")
	
	dataPortAddress   = response[firstBracketIndex + 1:lastBracketIndex]
	dataPortAddress   = dataPortAddress.split(",")
	
	data_host 	 = '.'.join(dataPortAddress[0:4])
	
	tempDataPort = dataPortAddress[-2:]
	data_port = (int(tempDataPort[0] * 256) + int(tempDataPort[1]))
	data_port = int(data_port)
	
	
	data_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	data_socket.connect((data_host,data_port))
	
	return data_socket

def download_file(bufferSize):
	
	downloadFolderName = "Downloads"
	
	if not os.path.exists(downloadFolderName):
		os.makedirs(downloadFolderName)
		
	if file_Name: 
		
		data_socket = dataConnection(bufferSize)
		
		
		file_data = data_socket.recv(bufferSize)
		f = open(downloadFolderName + "/" + file_Name, 'wb')
		
		while file_data:
			f.write(file_data)
			file_data = data_socket.recv(bufferSize)
			
		data_socket.close()