import os
import sys
import time
import socket
import string
import threading
from threading import Thread

from PyQt5 import QtCore, QtGui, QtWidgets
from ClientUI import Ui_ClientUI

class FTPClient:
	def __init__(self):
		self.IsConnected = False
		self.control_socket = None
		self.data_socket = None
		self.bufferSize = 8192
		self.clientID = ""
		self.IsValidUser = False
		self.ErrorCodes = ['530', '500', '501', '421', '403', '550']
	#_____________________________________________________________________
	# Function to initialize a TCP to the server
	def initializeFTPConnection(self, host_name):
		
		host_port = 21
		host_adr  = (host_name, host_port) 
		
		self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		try:
			self.control_socket.connect(host_adr)
			self.recv_command()
			print("=====================================================")
		except:
			
			print("Failed to connect to ", host_name )
			time.sleep(3)
			return
		self.IsConnected = True
		print("			Connected to Server				")
		
	#_____________________________________________________________________
	# Function to login to the server
	def login(self, username, password):
		
		command  = 'USER ' + username + '\r\n' 
		self.send_command( command )
		response = self.recv_command()
		
		if response[0] not in self.ErrorCodes:
			
			command  = 'PASS ' + password + '\r\n' 
			self.send_command(command)
			response = self.recv_command()
			
			if response[0] in self.ErrorCodes:
				self.IsValidUser = False
				
			self.IsValidUser = True
			self.clientID = username
		else:
			self.IsValidUser = False
	#_____________________________________________________________________
	# Function to sent a command to the server
	def send_command(self, command):
		print("Client: ", command)
		self.control_socket.send(command.encode())
	#_____________________________________________________________________
	# Function to get the list of files on the server's directory
	def getDirList(self):
		
		self.dataConnection()
		
		command = 'LIST\r\n'
		self.send_command( command)
		response = self.recv_command()
		
		if response[0] not in self.ErrorCodes: 
			
			file_data = self.data_socket.recv(self.bufferSize)
			while file_data:
				fileInfo = file_data.decode('utf-8')
				
				print(fileInfo.split(','))
				file_data = self.data_socket.recv(self.bufferSize)
				
		self.data_socket.close()
		response = self.recv_command()
	#_____________________________________________________________________
	# Function to receive the reply from the server
	def recv_command(self):
		response = self.control_socket.recv(8192).decode()
		responseCode, message = response.split(" ", 1)
		print("Server: " ,response)
		return responseCode, message
	#_____________________________________________________________________
	# Function to change the directory of the server
	def directory_change(self, directory):
		command = 'CWD ' + directory + '\r\n'
		self.send_command( command)
	#_____________________________________________________________________
	# Function to go up a directory in the server
	def directory_return(self):
		command = 'CDUP\r\n'
		self.send_command( command)
	#_____________________________________________________________________
	# Function to create a folder on the server
	def directory_create(self, directory):
		command = 'MKD ' + directory + '\r\n'
		self.send_command(self.client_socket, command)
	#_____________________________________________________________________
	# Function to delete a folder on the server
	def directory_delete(self, directory):
		command = 'RMD ' + directory + '\r\n'
		self.send_command(self.client_socket, command)
	#_____________________________________________________________________
	# Function to establish a Passive data connection
	def dataConnection(self):
		
		#PASV
		command  = 'PASV\r\n' 
		self.send_command( command)
		response = self.recv_command()
		
		response = response[1]
		firstBracketIndex = response.find("(")
		lastBracketIndex  = response.find(")")
		
		dataPortAddress   = response[firstBracketIndex + 1:lastBracketIndex]
		dataPortAddress   = dataPortAddress.split(",")
		
		data_host 	 = '.'.join(dataPortAddress[0:4])

		tempDataPort = dataPortAddress[-2:]
		
		data_port = int((int(tempDataPort[0]) * 256) + int(tempDataPort[1]))
		data_port = int(data_port)
		
		self.data_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.data_socket.connect((data_host,data_port))
	#_____________________________________________________________________
	# Function to download file from server to the downloads folder
	def download_file(self, file_Name):
		
		downloadFolderName = "Downloads"
		
		if not os.path.exists(downloadFolderName):
			os.makedirs(downloadFolderName)
			
		self.dataConnection()
		
		command  = 'RETR ' + file_Name + '\r\n' 
		self.send_command( command)
		response = self.recv_command()
		
		if response[0] not in self.ErrorCodes: 
			
			file_data = self.data_socket.recv(self.bufferSize)
			f = open(downloadFolderName + "/" + file_Name, 'wb')
			
			while file_data:
				f.write(file_data)
				file_data = self.data_socket.recv(self.bufferSize)
				
			f.close()
		else:
			return
		self.data_socket.close()
		
		response = self.recv_command()
	#_____________________________________________________________________
	# Function to upload a file to the server's current directory
	def upload_file(self, file_Name):
		
		
		if os.path.isfile(file_name):
			self.data_socket = self.dataConnection()
			
			command  = 'STOR ' + file_Name + '\r\n' 
			self.send_command( command)
			response = self.recv_command()
			
			file_Name = os.getcwd() + '/'+ file_Name
			
			uploadFile   = open(file_Name, 'rb')
			reading_data = uploadFile.read(self.bufferSize) 
			while reading_data:
				print(reading_data)
				self.data_socket.send(reading_data)
				reading_data = uploadFile.read(self.bufferSize) 
			
			uploadFile.close()
			self.data_socket.close()
			response = self.recv_command()
		else:
			print("File selected does not exist")
			return
	#_____________________________________________________________________
	# Function to logout of the server
	def logout(self):
		command = 'QUIT\r\n'
		self.send_command( command)
		response = self.recv_command()	
		self.control_socket.close()
	#_____________________________________________________________________
		
def main():

	client = FTPClient()
	
	username = ""
	password = ""
	host_name = ""
	
	host_name = input("Enter host IP address : ")
	
	client.initializeFTPConnection(host_name)
	
	if not client.IsConnected:
		return
	else:
		username = input(str("Enter user name : "))
		password = input(str("Enter user pass : "))
		client.login(username, password)
	
	if client.IsValidUser:
		#print("======================================================")
		client.getDirList()
		
		file_Name = input(str("Enter the name of the file you want to download : "))
		
		client.download_file(file_Name)
		
		print("======================================================")

		#client.getDirList()
		
		#file_Name = input(str("Enter the name of the file you want to upload : "))
		#client.upload_file(file_Name)
		
	client.logout()
	
if __name__ == '__main__':
		main()
