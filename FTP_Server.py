import os
import sys
import time
import socket
import random
import threading

class FTPServer (threading.Thread):
	def __init__(self, connection_socket, client_address, DataBase):
		threading.Thread.__init__(self)
		self.user = ' '
		self.cwd  = os.getcwd()                                        #current Working Directory
		self.dataBase = DataBase
		self.validUser = False
		self.commandConn = connection_socket
		self.dataConn 	 = None
		self.client_address = client_address
		self.cmdBufferSize  = 8192
		self.dataBufferSize = 8192
		self.isconnectionActive = True
		self.ActiveMode = False
		self.dataType = 'A'
	
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
			
			available_commands = ['USER', 'PASS', 'PASV', 'RETR', 'STOR', 'QUIT', 'PORT', 'TYPE', 'CWD']
			
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
					break
				else:
					reply = "500 Invalid password\r\n"
		self.send_response(reply)
		
	def TYPE(self,dataType):
		# set the data transfer type to ASCII(A) or Binary(I)
		self.dataType = dataType
		reply = "200 Type set to " + self.dataType +"\r\n"
		self.send_response(reply)
		
	def CWD(self, path):
		# Try change the current working directry
		newPath = self.cwd + '/' + str(path)
		if os.path.exists(newPath):
			reply = '250 Requested file action okay, completed.\r\n'
			self.cwd = newPath
		else:
			reply = '550 Requested action not taken. File/Directory unavailable\r\n'
		
		self.send_response(reply)
	
	def PWD(self):
		reply = "257 " + ' "' + self.cwd + '" ' + " is the current working directry\r\n"
		self.send_response(reply)
	
	def PASV(self):
		# Passive connection_socket, Disable Active mode
		self.ActiveMode = False
		host_name = socket.gethostbyname(socket.gethostname())
		
		# calculate a random port number between 12032 and 33023
		port_num1 = random.randint(47,128)
		port_num2 = random.randint(0,255)
		host_port = (port_num1 * 256) + port_num2
		
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
			
	def PORT(self, data_address):
		# Active mode connection
		self.ActiveMode = True

		data_address = data_address.split(',')
		host_IP = '.'.join(data_address[:4])
		
		port_num = data_address[-2:]
		host_port = int((int(port_num[0])*256 ) + port_num[1])
		
		host_adress = (host_IP, host_port)
		
		self.dataConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		try:
			
			self.dataConn.connect(host_adress)
			
			reply = "225 Entering Active mode\r\n"
			self.send_response(reply)
			
		except socket.error:
		
			reply = "425 Cannot open Data Connection\r\n"
			self.send_response(reply)
			

	def RETR(self, file_name):
	
		reply = "150 File status okay; about to open data connection\r\n"
		self.send_response(reply)
		
		# check the data connection mode (Active or Passive)
		if not self.ActiveMode:
			data_socket, data_address = self.dataConn.accept()
		
		# Locate and transfer the file
		filename = self.cwd + '/' + file_name
		file = open(filename, 'rb')
		reading = file.read(self.dataBufferSize)
		
		print("Accessing file: ", filename)
		while reading:
			print("Reading file ...")
			if not self.ActiveMode:
				data_socket.send(reading)
			else:
				self.dataConn.send(reading)
			reading = file.read(self.dataBufferSize)
			
		file.close()
		if not self.ActiveMode:
			data_socket.close()
		self.dataConn.close()
		
		reply = "226 Closeing data connection. Requested transfer action successful\r\n"
		self.send_response(reply)
		
	def STOR(self, filename):
		
		reply = "150 File status okay; about to open data connection\r\n"
		self.send_response(reply)
		
		if not self.ActiveMode:
			data_socket, data_address = self.dataConn.accept()
		
		filename = filename.replace('.','1.')
		
		file_name = self.cwd + '/' + filename
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
		
		reply = "226 Closeing data connection. Requested transfer action successful\r\n"
		self.send_response(reply)
		return
		
	def QUIT(self):
		# Disable the command socket connection
		self.isconnectionActive = False
		reply = "221 Goodbye\r\n"
		self.send_response(reply)
		self.commandConn.close()
		
	def Establish_data_conn(self, host_adress):
		# Establish a TCP connection
		data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		data_socket.bind(host_adress)
		data_socket.listen(1)
		return data_socket


def main():
	
	clientList  = "dataBase.txt"
	host_name   = socket.gethostbyname(socket.gethostname())
	host_port 	= 21
	host_adress = (host_name, host_port)
	print("Host : ", host_name, " port : ", host_port)
	
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(host_adress)
	
	
	while True:
		
		server_socket.listen(1)
		connection_socket, client_address = server_socket.accept()
		
		clientHandler = FTPServer( connection_socket, client_address, clientList)
		clientHandler.start()
		
if __name__ == '__main__':
		main()
