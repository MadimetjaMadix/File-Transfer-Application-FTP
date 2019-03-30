import os
import sys
import time
import socket
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
		self.cmdBufferSize  = 1024
		self.dataBufferSize = 8192
		self.isconnectionActive = True
		
		
	def run(self):
		print("Connection from : ", str(self.client_address))
		reply = "220 Welcome to FTP server\r\n"
		self.commandConn.send(reply.encode())
		
		while True:
			
			available_commands = ['USER', 'PASS', 'PASV', 'RETR', 'STOR', 'QUIT']
			
			client_message = elf.commandConn.recv(self.cmdBufferSize).decode()
			command  = client_message[:4].strip()
			argument = client_message[4:].strip()
			
			if not self.isconnectionActive:
				break
			
			if command in available_commands:
				
				ftp_command = getattr(self,command)
				if argument == '':
					ftp_command()
				else:
					ftp_command(argument)
			
			elif command not in available_commands:
				reply = "502 command not implemented\r\n"
				self.commandConn.send(reply.encode())
				
				
	def USER(self, username):
		
		file = open(self.dataBase, 'r')
		data = file.readlines()
		file.close()
		
		for userInfo in Data:
			validName, validPass = userInfo.split()
			if username == validName:
				self.user = username
				self.validUser = True
				reply = "331 password needed\r\n"
				self.commandConn.send(reply.encode())				
				return
				
		if not self.validUser:
			reply = "530 Invalid User\r\n"
			self.commandConn.send(reply.encode())
		
		
	def PASS(self, password):
		file = open(self.dataBase, 'r')
		data = file.readlines()
		file.close()
		
		if self.validUser:
			for userInfo in Data:
				validName, validPass = userInfo.split()
				if self.user == validName and password == validPass:
					reply = "230 Login successful\r\n"
					self.commandConn.send(reply.encode())
					
			reply = "530 Invalid password\r\n"
			self.commandConn.send(reply.encode())
			
	def PASV(self):
		return
		
	def RETR(self):
		return
		
	def STOR(self, argument):
		
		return
	def QUIT(self):
		self.isconnectionActive = False
		reply = "221 Goodbye\r\n"
		self.commandConn.send(reply.encode())
		self.commandConn.close()


def main():
	
	clientList  = "dataBase.txt"
	host_name   = socket.gethostbyname(socket.gethostname())
	host_port 	= 13000
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
