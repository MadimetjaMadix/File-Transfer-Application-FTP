import os
import sys
import time
import socket
import random
import string
import threading
from threading import Thread

from FTP_Client import FTPClient


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QTreeView, QWidget, QHBoxLayout, QApplication
from ClientUI import Ui_ClientUI

class clientUI_Interface(Ui_ClientUI):
	def __init__(self, ftpClientUIMain, ftpClient):
			Ui_ClientUI.__init__(self)
			self.setupUi(ftpClientUIMain)
			self.ftpClient = ftpClient
			
			self.progressBar.hide()
			self.Quit_pushButton.setEnabled(False)
			self.populateLocalDir()
			#---------------------------------
			self.connect_pushButton.clicked.connect(self.connectToServer)
			self.Quit_pushButton.clicked.connect(self.quit)
			
	def setStatus(self):
		if self.ftpClient.isError:
			self.status_label.setStyleSheet('color: red; font-family:Times New Roman')
			self.status_label.setText(str(self.ftpClient.server_response))
		else:
			self.status_label.setStyleSheet('color: blue; font-family:Times New Roman; font-size: 11pt')
		
		
	def connectToServer(self):
		if not self.ftpClient.IsConnected:
			self.ftpClient.initializeFTPConnection(str(self.lineEdit_host.text()))
			self.setStatus()
		self.loginToServer()
		if self.ftpClient.IsValidUser:
			self.status_label.setText(str("Online"))
			self.Quit_pushButton.setEnabled(True)
			self.connect_pushButton.setEnabled(False)
			self.connect_pushButton.setText("Connect")
		
	def loginToServer(self):
		if self.ftpClient.IsConnected:
			self.connect_pushButton.setText("Login")
			username = str(self.lineEdit_username.text())
			password = str(self.lineEdit_Password.text())
			self.ftpClient.login(username, password)
			self.setStatus()
			
	def populateLocalDir(self):
		
		Model = QFileSystemModel()
		Model.setRootPath(QtCore.QDir.rootPath())
		self.localDir_treeView.setModel(Model)
		self.localDir_treeView.setRootIndex(Model.index(r"C:\Users\sethosam\Documents\Networks"))
		
	def quit(self):
		if self.ftpClient.IsConnected:
			self.ftpClient.logout()
			self.Quit_pushButton.setEnabled(False)
			self.connect_pushButton.setEnabled(True)
			self.status_label.setStyleSheet('color: red; font-family:Times New Roman')
			self.status_label.setText(str("Offline"))
if __name__ == '__main__':

	app = QtWidgets.QApplication(sys.argv)
	ftpClientUIMain = QtWidgets.QMainWindow()
	ftpClient = FTPClient()
	prog = clientUI_Interface(ftpClientUIMain, ftpClient)
	ftpClientUIMain.show()
	sys.exit(app.exec_())