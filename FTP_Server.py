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
		
		
	def run(self):
		print("Connection from : ", str(self.client_address))
		reply = "220 Welcome to FTP server\r\n"
		print(reply)
		self.commandConn.send(reply.encode())
		
		while True:
			if not self.isconnectionActive:
				break
			
			available_commands = ['USER', 'PASS', 'PASV', 'RETR', 'STOR', 'QUIT']
			
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
				print(reply)
				self.commandConn.send(reply.encode())
				
				
	def USER(self, username):
		
		file = open(self.dataBase, 'r')
		data = file.readlines()
		file.close()
		
		# Check if user is in data-base
		for userInfo in data:
			validName, validPass = userInfo.split()
			if username == validName:
				self.user = username
				self.validUser = True
				reply = "331 password needed\r\n"
				print(reply)
				self.commandConn.send(reply.encode())				
				return
				
		if not self.validUser:
			reply = "530 Invalid User\r\n"
			print(reply)
			self.commandConn.send(reply.encode())
		
		
	def PASS(self, password):
		file = open(self.dataBase, 'r')
		data = file.readlines()
		file.close()
		
		# check USER and corrs pass in dataBase
		if self.validUser:
			for userInfo in data:
				validName, validPass = userInfo.split()
				if self.user == validName and password == validPass:
					reply = "230 Login successful\r\n"
					break
				else:
					reply = "500 Invalid password\r\n"
		self.commandConn.send(reply.encode())
			
	def PWD(self):
		reply = "257 " + "'self.cwd'" + " is the current working directry\r\n"
		print(reply)
		self.commandConn.send(reply.encode())
	
	def PASV(self):
		#passive connection_socket
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
			print(reply)
			self.commandConn.send(reply.encode())
		except:
			reply = "425 Cannot open Data Connection\r\n"
			print(reply)
			self.commandConn.send(reply.encode())
		
		
	def RETR(self, file_name):
		
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
		
		reply = "226 Data transfer complete\r\n"
		print(reply)
		self.commandConn.send(reply.encode())
		
		
	def STOR(self, filename):
		
		reply = "150 opening connection\r\n"
		print(reply)
		self.commandConn.send(reply.encode())
		
		#if not self.ActiveMode:
		data_socket, data_address = self.dataConn.accept()
		print("creating file..")
		
		filename = filename.replace('.','1.')
		
		file_name = self.cwd + '/' + filename
		file = open(file_name, 'wb')
		#if not self.ActiveMode:
		print("receiving data...")
		file_data = data_socket.recv(self.dataBufferSize)
		print(file_data)
		#else:
			#file_data = self.dataConn.recv(self.dataBufferSize)
			
		while file_data:
			print("receiving data...")
			file.write(file_data)
			#if not self.ActiveMode:
			file_data = data_socket.recv(self.dataBufferSize)
			#else:
				#file_data = self.dataConn.recv(self.dataBufferSize)
		
		file.close()
		#if not self.ActiveMode:
		data_socket.close()
		#self.dataConn.close()
		
		reply = "226 Data transfer complete\r\n"
		print(reply)
		#self.commandConn.send(reply.encode())
		return
		
	def QUIT(self):
		# Disable the command socket connection
		self.isconnectionActive = False
		reply = "221 Goodbye\r\n"
		self.commandConn.send(reply.encode())
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
