import os
import sys
import time
import socket
import random
import string
import threading
from threading import Thread

DownloadProgres = 0

class FTPClient:
	'''
	This class holds all the logic belonging to the FTPClient. This includes the User 
	Protocol Interpreter and the User Data Transfer Process.
	'''
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
		self.upLoadList = []
		self.downloadList = []
		self.progressValue = 0
		self.ErrorCodes = ['530', '500', '501', '421', '403', '550', '503']
	#_____________________________________________________________________
	# Function to initialize a TCP to the server
	def initializeFTPConnection(self, host_name):
		'''
		This Function initiate a control connection. This is the communication path 
		between the USER-PI and SERVER-PI for the exchange of commands and replies.
		This connection follows the Telnet Protocol.
		'''
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
		'''
		This function sends the user infomation to the server through comands 
		and checks the reply if is the user-information was valid.
		'''
		command  = 'USER ' + username + '\r\n' 
		self.send_command( command )
		response = self.recv_command()
		
		if response[0] not in self.ErrorCodes:
			
			command  = 'PASS ' + password + '\r\n' 
			self.send_command(command)
			response = self.recv_command()
			self.server_response = response[1]
			
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
		'''
		This function sends the commands to the server through the control socket.
		'''
		print("Client: ", command)
		try:
			self.control_socket.send(command.encode())
		except:
			msg = 'Failed to send to server'
			self.isError = True
			self.server_response = msg
			print(msg)
			self.IsConnected = False
			if self.isActive:
				self.data_connection.close()
			self.control_socket.close()
	#_____________________________________________________________________
	# Function to get the list of files on the server's directory
	def getDirList(self):
		'''
		This function request a list of files in the server's current directory
		and adds the to an array.
		'''
		self.isActive = False
		self.dataConnection()
		
		command = 'LIST\r\n'
		self.send_command( command)
		if self.IsConnected:
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
		This list modifies the list data to be stored in a specific maner.
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
		'''
		This function modified the filesize from bytes to compound sizes
		'''
		# Response is in bytes:
		kbSize        = 1024
		mbSize        = kbSize**2
		gbSize		  = kbSize**3
		newFileSize   = 0
		sizeType	  = 'Bytes'
		# Convert to megabytes when file is larger than a megabyte
		if fileSize < kbSize:
			newFileSize = fileSize
		elif fileSize >= kbSize and fileSize < mbSize:
			newFileSize = fileSize/kbSize
			sizeType    = 'KB'
		elif fileSize >= mbSize and fileSize < gbSize:
			newFileSize = fileSize/mbSize
			sizeType = 'MB'
		elif fileSize >= gbSize:
			newFileSize = fileSize/gbSize
			sizeType = 'GB'
		
		newFileSize = round(newFileSize,2)
		return newFileSize, sizeType
	
	#_____________________________________________________________________
	# Function to receive the reply from the server
	def recv_command(self):
		'''
		This function receives replys from the sever through the control socket
		and determines if an error code was recieved or not.
		'''
		response = self.control_socket.recv(8192).decode()
		responseCode, message = response.split(" ", 1)
		if responseCode not in self.ErrorCodes:
			self.isError = False
		else:
			self.isError = True
		print("Server: " ,response)
		return responseCode, message
	#_____________________________________________________________________
	# Function to change the directory of the server
	def directory_change(self, directory):
		'''
		This function send a comand to the server to change to the specified
		directory if it exists.
		'''
		command = 'CWD ' + directory + '\r\n'
		self.send_command( command)
		if self.IsConnected:
			response = self.recv_command()
			self.server_response = response[1]
	#_____________________________________________________________________
	# Function to go up a directory in the server
	def directory_return(self):
		'''
		This function sends a comand to the server to go move up the directory once.
		'''
		path = ".."
		try:
			pathIndex = self.serverDir.rfind("\\", 1)
			path = self.serverDir[:pathIndex+1]
			print(path)
		except:
			print(" ")
		command = 'CDUP ' + path +'\r\n'
		self.send_command( command)
		if self.IsConnected:
			response = self.recv_command()
			self.server_response = response[1]
	#_____________________________________________________________________
	# Function to go up a directory in the server
	def directory_print(self):
		'''
		This function sends a command to the server to return the current working
		directory.
		'''
		command = 'PWD\r\n'
		self.send_command( command)
		if self.IsConnected:
			response = self.recv_command()
			self.serverDir = response[1]
			
			indexFirstElement 	   = response[1].find('"')
			indexLastElement  	   = response[1].rfind('"')
		
			if indexFirstElement!=-1 and indexLastElement!=-1:
				self.serverDir   = self.serverDir[indexFirstElement+1:indexLastElement]
	#_____________________________________________________________________
	# Function to create a folder on the server
	def directory_create(self, directory):
		'''
		This function sends a command to the server to create a directory of a given 
		name if it does not exist.
		'''
		command = 'MKD ' + directory + '\r\n'
		self.send_command( command)
		if self.IsConnected:
			response = self.recv_command()
			self.server_response = response[1]
	#_____________________________________________________________________
	# Function to delete a file
	def file_delete(self, filename):
		'''
		This function sends a command to the server to delete a given file if 
		it exist.
		'''
		command = 'DELE ' + filename + '\r\n'
		self.send_command( command)
		if self.IsConnected:
			response = self.recv_command()
			self.server_response = response[1]
	#_____________________________________________________________________
	# Function to delete a folder on the server
	def directory_delete(self, directory):
		'''
		This function sends a command to the server to delete a given directory
		and all of its contents.
		'''
		command = 'RMD ' + directory + '\r\n'
		self.send_command( command)
		if self.IsConnected:
			response = self.recv_command()
			self.server_response = response[1]
	#_____________________________________________________________________
	# Function to establish a Passive data connection
	def dataConnection(self):
		'''
		This function sends a command to the server to establish a data connection.
		the connection is either PASSIVE or ACTIVE.
		'''
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
			if self.IsConnected:
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
	def download_file(self, file_Name, progress_callback=None):
		'''
		This function sends a command to the server to RETRIVE a given file
		through the data connection if it exists.
		'''
		downloadFolderName = "Downloads"
		
		if not os.path.exists(downloadFolderName):
			os.makedirs(downloadFolderName)
			
		self.dataConnection()
		
		command  = 'RETR ' + file_Name + '\r\n' 
		self.send_command( command)
		if self.IsConnected:
			response = self.recv_command()
			
			if response[0] not in self.ErrorCodes: 
				
				response = response[1]
				firstBracketIndex = response.find("(")
				lastBracketIndex  = response.find(")")
				
				filesize = response[firstBracketIndex + 1:lastBracketIndex]
				filesize, bytes = filesize.split(" ", 1)
				file_Size = int(filesize)
				
				file_data = self.data_socket.recv(self.bufferSize)
				f = open(downloadFolderName + "\\" + file_Name, 'wb')
				
				#temp = 8192
				i = 1
				while file_data:
					temp = int(((self.bufferSize*i)/file_Size)*100)
					DownloadProgres = temp
					self.progressValue = temp
					if progress_callback!=None:
						progress_callback.emit()
					
					#print(self.progressValue)
					f.write(file_data)
					
					file_data = self.data_socket.recv(self.bufferSize)
					i = i+1
				f.close()
				if file_Name in self.downloadList:
					self.downloadList.remove(file_Name)
		else:
			return
		self.data_socket.close()
		
		response = self.recv_command()
	def getProgressVal(self):
		return self.progressValue
	#_____________________________________________________________________
	# Function to upload a file to the server's current directory
	def upload_file(self, file_Name, filepath,   progress_callback=None):
		'''
		This function sends a command to the server to STORE a given file
		through the data connction on its current working directory.
		'''
		if self.IsConnected:
			print(file_Name)
			print(filepath)
			if os.path.isfile(filepath):
				self.dataConnection()
				fileSize = os.path.getsize(filepath)
				
				command  = 'STOR ' + file_Name + '\r\n' 
				self.send_command( command)
				response = self.recv_command()
				
				if response[0] not in self.ErrorCodes: 
					#file_Name = os.getcwd() + '/'+ file_Name
					
					uploadFile   = open(filepath, 'rb')
					reading_data = uploadFile.read(self.bufferSize) 
					temp  = self.bufferSize
					while reading_data:
						self.progressValue = int((temp/fileSize)*100)
						
						if progress_callback!=None:
							progress_callback.emit()
						
						self.data_socket.send(reading_data)
						reading_data = uploadFile.read(self.bufferSize) 
						temp = temp + self.bufferSize
						
					uploadFile.close()
					if file_Name in self.upLoadList:
						self.upLoadList.remove(file_Name)
					
					self.data_socket.close()
					response = self.recv_command()

			else:
				print("File selected does not exist")
				return
		else:
			msg = "Not connected to server"
			self.isError = True
			self.server_response = msg
			print(msg)
	#_____________________________________________________________________
	# Function to test the connection with the server
	def testConnectionToServer(self):
		return
	#_____________________________________________________________________
	# Function to logout of the server
	def logout(self):
		'''
		This function sends a command to the server to disable all the communication link
		both data and control connections.
		'''
		command = 'QUIT\r\n'
		self.send_command( command)
		if self.IsConnected:
			response = self.recv_command()
			self.IsConnected = False
			if self.isActive:
				self.data_connection.close()
			self.control_socket.close()
	#_____________________________________________________________________

