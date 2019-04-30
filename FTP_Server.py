import shutil, os
import sys
import time
import stat
import string
import socket
import random
import filecmp
import datetime
import threading 
import traceback
from threading import Thread

class FTPServer (threading.Thread):
	def __init__(self, connection_socket, client_address, DataBase,homeDir ):
		threading.Thread.__init__(self)
		self.user = ' '
		self.cwd  = homeDir                                        #current Working Directory
		self.homeDir = homeDir
		self.dataBase = homeDir + '\\' +DataBase
		self.validUser = False
		self.commandConn = connection_socket
		self.dataConn 	 = None
		self.client_address = client_address
		self.cmdBufferSize  = 8192
		self.dataBufferSize = 8192
		self.isconnectionActive = True
		self.ActiveMode = False
		self.dataType = 'l'
	
	def send_response(self,response):
		print(response)
		self.commandConn.send(response.encode())	
		
	def run(self):
		print("Connection from : ", str(self.client_address))
		reply = "220 Welcome to FTP server\r\n"
		self.send_response(reply)
		
		while True:
			if not self.isconnectionActive:
				break
			
			available_commands = ['USER', 'PASS', 'DELE' ,'PASV', 'RETR', 'STOR', 'QUIT', 'PORT', 'TYPE', 'PWD', 'CWD', 'LIST', 'CDUP', 'MKD', 'RMD' ]
			
			client_message = self.commandConn.recv(self.cmdBufferSize).decode()
			print("Client : ", client_message)
			command  = client_message[:4].strip()
			argument = client_message[4:].strip()
			
			# Check command and call respective fn if available
			if command in available_commands:
				
				ftp_command = getattr(self,command)
				if argument == '':
					ftp_command()
				else:
					ftp_command(argument)
			
			elif command not in available_commands:
				reply = "502 command not implemented\r\n"
				self.send_response(reply)
				
	
#begin User		
	def USER(self, username = 'user'):
		
		file = open(self.dataBase, 'r')
		data = file.readlines()
		file.close()
		
		# Check if user is in data-base
		for userInfo in data:
			validName, validPass = userInfo.split()
			if username == validName:
				self.user = username
				self.validUser = True
				
				reply = "331 password required for " + self.user + "\r\n"
				self.send_response(reply)
				return
				
		if not self.validUser:
			reply = "530 Invalid User\r\n"
			self.send_response(reply)
		
#end User

#begin Passive
	def PASS(self, password = 'pass'):
		file = open(self.dataBase, 'r')
		data = file.readlines()
		file.close()
		
		# check USER and the corrs pass are in dataBase
		if self.validUser:
			for userInfo in data:
				validName, validPass = userInfo.split()
				if self.user == validName and password == validPass:
					reply = "230 Login successful\r\n"
					self.createUserFolder()
					break
				else:
					reply = "500 Invalid password\r\n"
		self.send_response(reply)
#end Passive


	def createUserFolder(self):
		path = self.homeDir + "\\" + "HOME"
		if os.path.exists(path):
			os.chdir(path)
			self.cwd = os.getcwd()
		userFolder = "USERS" + "\\" +self.user
		if not os.path.exists(userFolder):
			os.makedirs(userFolder)

#begin Representation Type 
	def TYPE(self,dataType):
		# set the data transfer type to ASCII(A) or Binary(I)
		self.dataType = dataType
		reply = "200 Type set to " + self.dataType +"\r\n"
		self.send_response(reply)
#end Representation Type 

#begin Change to Parent Directory  
	def CDUP(self, path):
		# Try to go up one directory
		
		#dirname, filename = os.path.split(self.homeDir)
		dirname = self.homeDir + "\\"
		print("home Dir :",dirname)
		print("requested Dir :",path)
		if os.path.exists(path) and not  path == dirname:
			os.chdir(path)
			self.cwd  = os.getcwd()
			reply = "200 current working directry is " + self.cwd +"\r\n"
			self.send_response(reply)
		else:
			reply = "550 Requested action not taken. File/Directory unavailable\r\n"
			self.send_response(reply)
#end Change to Parent Directory

#begin Make directory
	def MKD(self, directory):
		# Try make new directory
		reply = ""
		userDir = self.homeDir + "\\" + "HOME" + "\\" + "USERS"
		if not (self.cwd ==  userDir):
			if not os.path.exists(directory):
				os.makedirs(directory)
			reply = "257 directory " + directory + " is created\r\n"
		else:
			reply = "550 Permission denied\r\n"
		
		self.send_response(reply)
#end Make directory
		
#begin Remove directory
	def RMD (self,directory):
		
		# Try remove a directory
		userDir = self.homeDir + "\\" + "HOME" + "\\" + "USERS"
		reply = ""
		if os.path.exists(directory):
			if not (directory==userDir):
				if not (self.cwd==userDir):
					if os.path.isdir(directory):
						try:
							shutil.rmtree(directory)
							reply = "250 file " + directory + " is removed\r\n"
						except OSError:
							reply = "500 error while removing  the file\r\n"
				else:
					reply = "550 Permission denied\r\n"
			else:
				reply = "550 Permission denied\r\n"
		else:
			reply = "550 Requested action not taken. Directory unavailable\r\n"
			
		self.send_response(reply)
#end Remove directory
		
#begin delete
	def DELE (self, pathname):
	# Try remove a file
		pathname.replace( r"Home", self.homeDir)
		reply = ""
		if os.path.exists(pathname):
			if os.path.isfile(pathname): 
				try:
					os.remove(pathname)
					reply = "250 file " + pathname + " is removed\r\n"
				except OSError:
					reply = "500 error while removing  the file\r\n"
		else:
			reply = "550 Requested action not taken. File unavailable\r\n"
		self.send_response(reply)
#end delete

#begin Change working directory
	def CWD(self, path):
		# Try change the current working directry
		reply = ''
		if os.path.exists(path):
			userDir = self.homeDir + "\\" + "HOME" + "\\" + "USERS" 
			directory, filename = os.path.split(path)
			if (userDir == directory):
				if (filename == self.user):
					os.chdir(path)
					self.cwd = os.getcwd()
					reply = '250 Requested file action okay, completed.\r\n'
				else:
					reply = "550 Permission denied\r\n"
			else:
				os.chdir(path)
				self.cwd = os.getcwd()
				reply = '250 Requested file action okay, completed.\r\n'
				
		else:
			reply = '550 Requested action not taken. File/Directory unavailable\r\n'
		
		self.send_response(reply)
#end Change working directory

#begin Print working directory
	def PWD(self):
		path = self.cwd + '\\'
		print("Path :", path)
		print("home dir : ", self.homeDir)
		path.replace(self.homeDir, r"Home")
		print("path after : ", path)
		reply = "257 " + self.cwd + "\r\n"
		self.send_response(reply)
#end Print working directory

#begin List
	def LIST(self):
		
		reply = "125 List being send to Dataconnection\r\n"
		self.send_response(reply)
		data_socket, data_address = self.dataConn.accept()
		
		response = []
		if os.path.exists(self.cwd ):
			items = os.listdir(self.cwd )
			for file in items:
				newPath = os.path.join(self.cwd ,file)
				date_mod = datetime.datetime.fromtimestamp(os.path.getmtime(newPath)).strftime('%b %d %H:%M')
				fileSize = os.path.getsize(newPath)
				file_data = str(stat.filemode(os.stat(newPath).st_mode))+'\t'+'1 4006 \t 4000\t\t'+str(fileSize)+'\t'+str(date_mod)+'\t'+file 
				response.append(file_data)
		
		for item in response:
			data_socket.send((item+'\r\n').encode())
			
		reply = "200 Listing completed\r\n"
		self.send_response(reply)
#end List

#begin Passive
	def PASV(self):
		# Passive connection_socket, Disable Active mode
		self.ActiveMode = False
		host_name = socket.gethostbyname(socket.gethostname())
		
		# calculate a random port number between 12032 and 33023
		port_num1 = random.randint(47,128)
		port_num2 = random.randint(0,255)
		host_port = int((int(port_num1) * 256) + int(port_num2))
		
		host_adress = (host_name,host_port)
		
		server_address = host_name.split(".")
		server_address = ','.join(server_address)
		server_address = "(" + server_address + "," + str(port_num1) +"," + str(port_num2) + ")"
		
		# Try to establish a socket connection
		try:
			self.dataConn = self.Establish_data_conn(host_adress)
			
			reply = "227 Entering Passive Mode " + str(server_address) + "\r\n"
			self.send_response(reply)
			
		except socket.error:
		
			reply = "425 Cannot open Data Connection\r\n"
			self.send_response(reply)
#end Passive
			
#begin Data port		
	def PORT(self, data_address):
		# Active mode connection
		self.ActiveMode = True

		data_address = data_address.split(',')
		host_IP = '.'.join(data_address[:4])
		
		port_num = data_address[-2:]
		host_port = int((int(port_num[0])*256 ) + int(port_num[1]))
		
		host_adress = (host_IP, host_port)
		
		self.dataConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		try:
			
			self.dataConn.connect(host_adress)
			
			reply = "225 Entering Active mode\r\n"
			self.send_response(reply)
			
		except socket.error:
		
			reply = "425 Cannot open Data Connection\r\n"
			self.send_response(reply)
#end Data port
			
#begin Retrive
	def RETR(self, file_name):
		reply = ""
		try:
			clientThread = Thread(target=(self.retriveFile), args=(file_name,))
			clientThread.start()
			clientThread.join()
		except Exception:
			print("Error while creating a thread")
			reply = "550 request action not taken"
		self.send_response(reply)
#end Retrive
			
#Begin Download
	def retriveFile(self, file_name):
		# returns data to the client.
		reply = ""
		if os.path.isfile(file_name):
			reply = "150 opening " + self.dataType + " mode data connection for " + file_name + "(" + str(os.path.getsize(file_name))+ " bytes)\r\n"
			self.send_response(reply)
			
			# check the data connection mode (Active or Passive)
			if not self.ActiveMode:
				data_socket, data_address = self.dataConn.accept()
			
			# Locate and transfer the file
			filename = self.cwd + '\\' + file_name

			file = open(filename, 'rb')
			reading = file.read(self.dataBufferSize)
			
			print("Accessing file: ", filename)
			print("Reading file ...")
			while reading:
				
				if not self.ActiveMode:
					data_socket.send(reading)
				else:
					self.dataConn.send(reading)
				reading = file.read(self.dataBufferSize)
				
			file.close()
			if not self.ActiveMode:
				data_socket.close()
			self.dataConn.close()
			
			reply = "226 Closing data connection. Requested transfer action successful\r\n"
		else:
			reply = "550 The system cannot find the file specified.\r\n"
			
		self.send_response(reply)
#end downloading
		
#begin Store
	def STOR(self, filename):
		reply = ""
		try:
			clientThread = Thread(target=(self.storeFile), args=(filename,))
			clientThread.start()
			clientThread.join()
		except Exception:
			print("Error while creating a thread")
			reply = "550 request action not taken"
		self.send_response(reply)
#end Store

#beging Upload
	def storeFile(self, filename):
	# STORES data on the server
		reply = "150 File status okay; about to open data connection\r\n"
		self.send_response(reply)
	
		if not self.ActiveMode:
			data_socket, data_address = self.dataConn.accept()
		
		
		file_name = self.cwd + '\\' + filename
		file = open(file_name, 'wb')
		if not self.ActiveMode:
			file_data = data_socket.recv(self.dataBufferSize)
		else:
			file_data = self.dataConn.recv(self.dataBufferSize)
		
		while file_data:
			
			file.write(file_data)
			if not self.ActiveMode:
				file_data = data_socket.recv(self.dataBufferSize)
			else:
				file_data = self.dataConn.recv(self.dataBufferSize)
		
		file.close()
		if not self.ActiveMode:
			data_socket.close()
		self.dataConn.close()
		
		reply = "226 Closing data connection. Requested transfer action successful\r\n"
		self.send_response(reply)
		return
#end Upload
		
#begin Logout
	def QUIT(self):
		# Disable the command socket connection
		os.chdir(self.homeDir)
		self.isconnectionActive = False
		reply = "221 Goodbye\r\n"
		self.send_response(reply)
		self.commandConn.close()
#end Logout

#begin Establish_data_conn
	def Establish_data_conn(self, host_adress):
		# Establish a TCP connection
		data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		data_socket.bind(host_adress)
		data_socket.listen(1)
		return data_socket
#end Establish_data_conn

def main():
	homeFolder = "HOME"
	if not os.path.exists(homeFolder):
		os.makedirs(homeFolder)
	
	clientList  = ".dataBase.txt"
	host_name   = socket.gethostbyname(socket.gethostname())
	host_port 	= 21
	host_adress = (host_name, host_port)
	print("Host : ", host_name, " port : ", host_port)
	homeDir =os.getcwd()
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(host_adress)
	
	
	while True:
		
		server_socket.listen(1)
		connection_socket, client_address = server_socket.accept()
		clientHandler = FTPServer( connection_socket, client_address, clientList,homeDir )
		clientHandler.start()
		
if __name__ == '__main__':
		main()
