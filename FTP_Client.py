import os
import sys
import time
import socket
import threading
from threading import Thread

from PyQt5 import QtCore, QtGui, QtWidgets
from ClientUI import Ui_ClientUI

class FTPClient:
	def __init__(self):
		self.control_socket = None
		self.data_socket = None
		self.bufferSize = 8192
		self.clientID = ""
		self.IsValidUser = False
	
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
		print("			Connected to Server				")
		

	def login(self, username, password):
		
		command  = 'USER ' + username + '\r\n' 
		self.send_command( command )
		response = self.recv_command()
		
		ErrorCodes = ['530', '500', '501', '421', '403']
		if response[0] not in ErrorCodes:
			
			command  = 'PASS ' + password + '\r\n' 
			self.send_command(command)
			response = self.recv_command()
			
			if response[0] in ErrorCodes:
				self.IsValidUser = False
				
			self.IsValidUser = True
			self.clientID = username
		else:
			self.IsValidUser = False
			

	 
	def send_command(self, command):
		print("Client: ", command)
		self.control_socket.send(command.encode())
		
	def getDirList(self):
		
		self.dataConnection()
		
		command = 'LIST\r\n'
		self.send_command( command)
		response = self.recv_command()
		dirList = response[1].split(',')
		
		for items in dirList:
			print(items)
		
		
	def recv_command(self):
		response = self.control_socket.recv(8192).decode()
		responseCode, message = response.split(" ", 1)
		print("Server: " ,response)
		return responseCode, message

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


	def download_file(self, file_Name):
		
		downloadFolderName = "Downloads"
		
		if not os.path.exists(downloadFolderName):
			os.makedirs(downloadFolderName)
			
		self.data_socket = self.dataConnection()
		
		command  = 'CWD ' + file_Name + '\r\n' 
		self.send_command( command)
		response = self.recv_command()
		
		command  = 'RETR ' + file_Name + '\r\n' 
		self.send_command( command)
		response = self.recv_command()
		
		if file_Name: 
			
			file_data = self.data_socket.recv(self.bufferSize)
			f = open(downloadFolderName + "/" + file_Name, 'wb')
			
			while file_data:
				f.write(file_data)
				file_data = self.data_socket.recv(self.bufferSize)
				
			f.close()
			self.data_socket.close()
			
		response = self.recv_command()
			
	def upload_file(self, file_Name):
		
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
		
	def logout(self):
		command = 'QUIT\r\n'
		self.send_command( command)
		response = self.recv_command()	
		self.control_socket.close()
	
		
def main():

	client = FTPClient()
	
	username = ""
	password = ""
	host_name = ""
	
	host_name = input("Enter host IP address : ")
	
	client.initializeFTPConnection(host_name)
	
	username = input(str("Enter user name : "))
	password = input(str("Enter user pass : "))
	client.login(username, password)
	
	if client.IsValidUser:
		#print("======================================================")
		
		#file_Name = "dataBase.txt"
		
		#download_file(file_Name, self.bufferSize,self.control_socket)
		
		print("======================================================")

		#client.getDirList()
		
		file_Name = "dataBase.txt"
		client.upload_file(file_Name)
		
	client.logout()
	
if __name__ == '__main__':
		main()
