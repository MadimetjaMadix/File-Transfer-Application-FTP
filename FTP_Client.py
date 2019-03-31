import os
import sys
import time
import socket
import threading
from threading import Thread


def initializeFTPConnection(host_name):
	
	host_port = 21
	host_adr  = (host_name, host_port) 
	
	control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	try:
		control_socket.connect(host_adr)
		recv_command(control_socket)
		print("=====================================================")
	except:
		
		print("Failed to connect to ", host_name )
		time.sleep(3)
		return
	print("				Connected to Server					")	
	return control_socket

def login( username, password,control_socket):
	
	#control_socket = initializeFTPConnection(socket.gethostname())
	
	command  = 'USER ' + username + '\r\n' 
	send_command(control_socket, command)
	response = recv_command(control_socket)
	
	ErrorCodes = ['530', '500', '501', '421', '403']
	if response[0] not in ErrorCodes:
		
		command  = 'PASS ' + password + '\r\n' 
		send_command(control_socket, command)
		response = recv_command(control_socket)
		
		if response[0] in ErrorCodes:
			return False
			
		return True
	else:
		return False
		

 
def send_command(control_socket, command):
	print("Client: ", command)
	control_socket.send(command.encode())

	
def recv_command(control_socket):
	response = control_socket.recv(8192).decode()
	responseCode, message = response.split(" ", 1)
	print("Server: " ,response)
	return responseCode, message

def dataConnection(bufferSize,control_socket):
	
	#PASV
	command  = 'PASV\r\n' 
	send_command(control_socket, command)
	response = recv_command(control_socket)
	
	response = response[1]
	firstBracketIndex = response.find("(")
	lastBracketIndex  = response.find(")")
	
	dataPortAddress   = response[firstBracketIndex + 1:lastBracketIndex]
	dataPortAddress   = dataPortAddress.split(",")
	
	data_host 	 = '.'.join(dataPortAddress[0:4])

	tempDataPort = dataPortAddress[-2:]
	
	data_port = int((int(tempDataPort[0]) * 256) + int(tempDataPort[1]))
	data_port = int(data_port)
	
	
	data_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	data_socket.connect((data_host,data_port))

	return data_socket

def download_file(file_Name, bufferSize,control_socket):
	
	downloadFolderName = "Downloads"
	
	if not os.path.exists(downloadFolderName):
		os.makedirs(downloadFolderName)
		
	data_socket = dataConnection(bufferSize,control_socket)
		
	command  = 'RETR ' + file_Name + '\r\n' 
	send_command(control_socket, command)
	response = recv_command(control_socket)
	
	if file_Name: 
		
		file_data = data_socket.recv(bufferSize)
		f = open(downloadFolderName + "/" + file_Name, 'wb')
		
		while file_data:
			f.write(file_data)
			file_data = data_socket.recv(bufferSize)
			
		data_socket.close()
		
def upload_file(file_Name, bufferSize,control_socket):
	
	data_socket = dataConnection(bufferSize,control_socket)
	
	command  = 'STOR ' + file_Name + '\r\n' 
	send_command(control_socket, command)
	response = recv_command(control_socket)
	
	file_Name = os.getcwd() + '/'+ file_Name
	
	uploadFile   = open(file_Name, 'rb')
	reading_data = uploadFile.read(bufferSize) 
	
	while reading_data:
		print("Sending data...")
		data_socket.send(reading_data)
		reading_data = uploadFile.read(bufferSize) 
	
	uploadFile.close()
	print("Done. file closed")
	data_socket.close()
	
def logout(control_socket):
	command = 'QUIT\r\n'
	send_command(control_socket, command)
	response = recv_command(control_socket)	
	control_socket.close()
	
		
def main():
	
	bufferSize = 8192
	
	host_name = socket.gethostbyname(socket.gethostname())
	
	control_socket = initializeFTPConnection(host_name)
	
	username = input(str("Enter user name : "))
	password = input(str("Enter user pass : "))
	Login_is_valid = login(username, password,control_socket)
	
	if Login_is_valid:
		#print("======================================================")
		
		#file_Name = "dataBase.txt"
		
		#download_file(file_Name, bufferSize,control_socket)
		
		print("======================================================")
		file_Name = "dataBase.txt"
		upload_file(file_Name, bufferSize,control_socket)
		
	logout(control_socket)
	
if __name__ == '__main__':
        main()
