import os
import sys
import time
import socket
import random
import string
import threading
from threading import Thread

from PyQt5 import QtCore, QtGui, QtWidgets
from ClientUI import Ui_ClientUI

class FTPClient:
	def __init__(self):
		self.IsConnected = False
		self.isActive = False
		self.control_socket = None
		self.data_socket = None
		self.data_connection = None
		self.bufferSize = 8192
		self.clientID = ""
		self.IsValidUser = False
		self.server_response = ""
		self.isError = False
		self.ListInDir = []
		self.serverDir = ''
		self.ErrorCodes = ['530', '500', '501', '421', '403', '550', '503']
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
			message = str("Failed to connect to " + host_name )
			self.isError = True
			self.server_response = message
			print(message)
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
			else:
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
		
		self.isActive = False
		self.dataConnection()
		
		command = 'LIST\r\n'
		self.send_command( command)
		response = self.recv_command()
		
		if response[0] not in self.ErrorCodes: 
			
			if self.isActive:
				file_data = self.data_connection.recv(self.bufferSize).decode('utf-8').rstrip()
			else:
				file_data = self.data_socket.recv(self.bufferSize).decode('utf-8').rstrip()
			self.ListInDir = []
			while file_data:
				fileInfo = file_data.split('\r')
				for item in fileInfo:
					item = item.strip().rstrip()
					self.modifyListDetails(item)
				#print(fileInfo.split(','))
				if self.isActive:
					file_data = self.data_connection.recv(self.bufferSize).decode('utf-8').rstrip()
				else:
					file_data = self.data_socket.recv(self.bufferSize).decode('utf-8').rstrip()
		if not self.isActive:
			self.data_socket.close()
		print(self.ListInDir)
		response = self.recv_command()
		
	def modifyListDetails(self,listData):
		'''
			modifyListDetails 
		'''
		filePermission = 0
		filenameIndex  = 8
		fileSizeIndex  = 4
		fileLastModifiedIndexFirst = 5
		fileLastModifiedIndexLast  = 8
		
		# Split into columns:
		temp = listData.split()
		# Select file name:
		filename = ' '.join(temp[filenameIndex:])
		# Select file size:
		fileSize = None
		try:
			fileSize = float(' '.join(temp[fileSizeIndex:fileSizeIndex+1]))
			tempFileSize = self.processFileSize(fileSize)
			fileSize = str(tempFileSize[0])+' '+tempFileSize[1] 
		except:
			print("error on ",fileSizeIndex)
	
		# Select last modified details:
		lastModified = ' '.join(temp[fileLastModifiedIndexFirst:fileLastModifiedIndexLast])
		
		# Select permissions:
		permissions = ' '.join(temp[filePermission:filePermission+1])
		
		# add to list:
		tempList = [filename, fileSize, lastModified, permissions]
		
		# Remove empty fields:
		tempList = list(filter(None, tempList))
		
		self.ListInDir.append(tempList)
	
	def processFileSize(self, fileSize):
		# Response is in bytes:
		
		kbSize        = 1024
		mbSize        = kbSize**2
		newFileSize   = 0
		sizeType	  = 'Bytes'
		# Convert to megabytes when file is larger than a megabyte
		if fileSize < kbSize:
			newFileSize = fileSize
		elif fileSize >= kbSize and fileSize < mbSize:
			newFileSize = fileSize/kbSize
			sizeType    = 'KB'
		elif fileSize >= mbSize:
			newFileSize = fileSize/mbSize
			sizeType = 'MB'
		
		newFileSize = round(newFileSize,2)
		return newFileSize, sizeType
	
	#_____________________________________________________________________
	# Function to receive the reply from the server
	def recv_command(self):
		response = self.control_socket.recv(8192).decode()
		responseCode, message = response.split(" ", 1)
		self.server_response = message
		if responseCode not in self.ErrorCodes:
			self.isError = False
		else:
			self.isError = True
		print("Server: " ,response)
		return responseCode, message
	#_____________________________________________________________________
	# Function to change the directory of the server
	def directory_change(self, directory):
		command = 'CWD ' + directory + '\r\n'
		self.send_command( command)
		response = self.recv_command()
	#_____________________________________________________________________
	# Function to go up a directory in the server
	def directory_return(self):
		print(self.serverDir)
		path = ".."
		try:
			pathIndex = self.serverDir.rfind("/", 1)
			path = self.serverDir[:pathIndex+1]
			print(path)
		except:
			print(" ")
		command = 'CDUP ' + path +'\r\n'
		self.send_command( command)
		response = self.recv_command()
	#_____________________________________________________________________
	# Function to go up a directory in the server
	def directory_print(self):
		command = 'PWD\r\n'
		self.send_command( command)
		response = self.recv_command()
		self.serverDir = response[1]
		
		indexFirstElement 	   = response[1].find('"')
		indexLastElement  	   = response[1].rfind('"')
	
		if indexFirstElement!=-1 and indexLastElement!=-1:
			self.serverDir   = self.serverDir[indexFirstElement+1:indexLastElement]
	#_____________________________________________________________________
	# Function to create a folder on the server
	def directory_create(self, directory):
		command = 'MKD ' + directory + '\r\n'
		self.send_command( command)
		response = self.recv_command()
	#_____________________________________________________________________
	# Function to delete a file
	def file_delete(self, filename):
		command = 'DELE ' + filename + '\r\n'
		self.send_command( command)
		response = self.recv_command()
	#_____________________________________________________________________
	# Function to delete a folder on the server
	def directory_delete(self, directory):
		command = 'RMD ' + directory + '\r\n'
		self.send_command( command)
		response = self.recv_command()
	#_____________________________________________________________________
	# Function to establish a Passive data connection
	def dataConnection(self):
		
		if self.isActive:
			#Active
			
			# calculate a random port number between 12032 and 33023
			port_num1 = random.randint(47,128)
			port_num2 = random.randint(0,255)
			host_port = (port_num1 * 256) + port_num2
			
			host_name = socket.gethostbyname(socket.gethostname())
			host_adress = (host_name,host_port)
			
			server_address = host_name.split(".")
			server_address = ','.join(server_address)
			server_address = server_address + "," + str(port_num1) +"," + str(port_num2)
			
			# Creates the data socket by listening for the connection
			data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			data_socket.bind((host_name, host_port))
			data_socket.listen(5)
			
			# Sends the PORT commands and tuple to the server
			command = 'PORT ' + server_address + '\r\n'
			self.send_command( command)
			response = self.recv_command()

			# Accepts the connection from the server
			self.data_connection, address_ip = data_socket.accept()
			
		else:
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
		
		print(file_Name)
		if os.path.isfile(file_Name):
			self.dataConnection()
			
			command  = 'STOR ' + file_Name + '\r\n' 
			self.send_command( command)
			response = self.recv_command()
			
			if response[0] not in self.ErrorCodes: 
				file_Name = os.getcwd() + '/'+ file_Name
				
				uploadFile   = open(file_Name, 'rb')
				reading_data = uploadFile.read(self.bufferSize) 
				while reading_data:
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
		self.IsConnected = False
		if self.isActive:
			self.data_connection.close()
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
		#client.getDirList()
		#client.directory_create("New")
		#client.getDirList()
		#client.directory_change("New")
		#command = 'PWD\r\n'
		#client.send_command( command)
		#response = client.recv_command()
		
		#client.directory_return()
		#command = 'PWD\r\n'
		#client.send_command( command)
		#response = client.recv_command()
		
		#client.directory_delete("New")
		client.getDirList()
		file_Name = input(str("Enter the name of the file you want to download : "))
		
		client.download_file(file_Name)
		
		print("======================================================")

		client.getDirList()
		
		file_Name = input(str("Enter the name of the file you want to upload : "))
		client.upload_file(file_Name)
		
	client.logout()
	
if __name__ == '__main__':
		main()
