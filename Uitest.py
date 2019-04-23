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
			self.localDir_treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
			self.localDir_treeView.customContextMenuRequested.connect(self.localMenu)
			
			self.remoteDir_tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
			self.remoteDir_tableWidget.customContextMenuRequested.connect(self.remoteMenu)
			
			#-----------------remote-------------------
			self.progressBar.hide()
			self.Quit_pushButton.setEnabled(False)
			self.btn_refreshRemoteDir.setEnabled(False)
			self.remoteDir_tableWidget.setEnabled(False)
			self.dirName_lineEdit.setEnabled(False)
			self.btn_createDir.setEnabled(False)
			self.btn_Cancell_createDir.setEnabled(False)
			self.updateServerDirectoryList()
			#-----------------Local-------------------
			self.populateLocalDir()
			
			#---------------------------------
			self.connect_pushButton.clicked.connect(self.connectToServer)
			self.Quit_pushButton.clicked.connect(self.quit)
			self.btn_refreshRemoteDir.clicked.connect(self.refreshRemote)
			self.btn_RefreshLocalDir.clicked.connect(self.refreshLocal)
			self.btn_createDir.clicked.connect(self.createDir)
			self.btn_Cancell_createDir.clicked.connect(self.disableFolderEdit)
			
	def setStatus(self):
		if self.ftpClient.isError:
			self.status_label.setStyleSheet('color: red; font-family:Times New Roman')
			self.status_label.setText(str(self.ftpClient.server_response))
		else:
			self.status_label.setStyleSheet('color: blue; font-family:Times New Roman; font-size: 11pt')
		statThread = Thread(target = self.updateStatus )
		statThread.run()
		
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
			self.btn_refreshRemoteDir.setEnabled(True)
			self.remoteDir_tableWidget.setEnabled(True)
			self.ftpClient.getDirList()
			self.updateServerDirectoryList()
		
	def loginToServer(self):
		if self.ftpClient.IsConnected:
			self.connect_pushButton.setText("Login")
			username = str(self.lineEdit_username.text())
			password = str(self.lineEdit_Password.text())
			self.ftpClient.login(username, password)
			self.setStatus()
			
	def populateLocalDir(self):
		
		self.localModel = QFileSystemModel()
		self.localModel.setRootPath(QtCore.QDir.rootPath())
		self.localDir_treeView.setModel(self.localModel)
		self.localDir_treeView.setRootIndex(self.localModel.index(r"C:\Users\sethosam\Documents\Networks"))
		self.localDir_treeView.setSortingEnabled(True)
		
	def localMenu(self):
		local_menu = QtWidgets.QMenu()
		fileUpload = local_menu.addAction("Upload")
		fileUpload.triggered.connect(self.uploadFile)
		cursor = QtGui.QCursor()	#privide a cursor location
		local_menu.exec_(cursor.pos())	# pass it to the menu executor
		
	def uploadFile(self):
		local_index = self.localDir_treeView.currentIndex()
		file_name = self.localModel.fileName(local_index)
		
		self.ftpClient.upload_file(file_name)
		print("Upload file : " + file_name)
		self.setStatus()
		
	def remoteMenu(self):
		remote_menu = QtWidgets.QMenu()
		fileDownload = remote_menu.addAction("Download")
		fileDownload.triggered.connect(self.downloadFile)
		fileDownload = remote_menu.addAction("Open")
		fileDownload.triggered.connect(self.openFolder)
		fileDownload = remote_menu.addAction("Delete")
		fileDownload.triggered.connect(self.deleteFile)
		fileDownload = remote_menu.addAction("New Folder")
		fileDownload.triggered.connect(self.enableFolderEdit)
		cursor = QtGui.QCursor()
		remote_menu.exec_(cursor.pos())
		
	def deleteFile(self):
		for currentQTableWidgetRow in self.remoteDir_tableWidget.selectionModel().selectedRows():
			if currentQTableWidgetRow.row()!=0:
				try:
					filename = self.remoteDir_tableWidget.item(currentQTableWidgetRow.row(), 0).text()
					permission = self.remoteDir_tableWidget.item(currentQTableWidgetRow.row(), 3).text()
					if permission.find('d') is not -1:
						path = self.addPath(filename)
						self.ftpClient.directory_delete(path)
						self.refreshRemote()
						self.setStatus()
					else:
						path = self.addPath(filename)
						self.ftpClient.file_delete(path)
						self.refreshRemote()
				except:
					self.status_label.setStyleSheet('color: red; font-family:Times New Roman')
					self.status_label.setText(str("Cant delete File"))
					return
					
	def enableFolderEdit(self):
		self.dirName_lineEdit.setEnabled(True)
		self.btn_createDir.setEnabled(True)
		self.btn_Cancell_createDir.setEnabled(True)
		self.btn_refreshRemoteDir.setEnabled(False)
		self.remoteDir_tableWidget.setEnabled(False)
		
	def disableFolderEdit(self):
		self.btn_Cancell_createDir.setEnabled(False)
		self.dirName_lineEdit.setEnabled(False)
		self.btn_createDir.setEnabled(False)
		self.btn_refreshRemoteDir.setEnabled(True)
		self.remoteDir_tableWidget.setEnabled(True)
		
	def createDir(self):
		self.dirName_lineEdit.setFocus()
		directoryName = str(self.dirName_lineEdit.text())
		self.dirName_lineEdit.clear()
		self.ftpClient.directory_create(directoryName)
		self.disableFolderEdit()
		self.setStatus()
		self.refreshRemote()
		return

	def addPath(self,filename):
		self.ftpClient.directory_print()
		print(self.ftpClient.serverDir)
		self.ftpClient.serverDir = self.ftpClient.serverDir.replace('\r\n', '')
		s = '/'
		path = self.ftpClient.serverDir + s + filename
		path = [self.ftpClient.serverDir,str(filename)]
		path = '/'.join(path)
		return path
	def openFolder(self):
		for currentQTableWidgetRow in self.remoteDir_tableWidget.selectionModel().selectedRows():
			if currentQTableWidgetRow.row()!=0:
				try:
					filename = self.remoteDir_tableWidget.item(currentQTableWidgetRow.row(), 0).text()
					permission = self.remoteDir_tableWidget.item(currentQTableWidgetRow.row(), 3).text()
					if permission.find('d') is not -1:
						path = self.addPath(filename)
						print('path :',path)
						self.ftpClient.directory_change(path)
						self.refreshRemote()
					else:
						self.status_label.setStyleSheet('color: red; font-family:Times New Roman')
						self.status_label.setText(str("Cant open file, Download instead"))
				except:
					self.status_label.setStyleSheet('color: red; font-family:Times New Roman')
					self.status_label.setText(str("Cant open file, Download instead"))
					
			else:
				self.ftpClient.directory_return()
				self.ftpClient.directory_print()
				self.refreshRemote()
		
	def downloadFile(self):
		for currentQTableWidgetRow in self.remoteDir_tableWidget.selectionModel().selectedRows():
			if currentQTableWidgetRow.row()!=0:
				try:
					filename = self.remoteDir_tableWidget.item(currentQTableWidgetRow.row(), 0).text()
					self.ftpClient.download_file(filename)
				except:
					self.status_label.setStyleSheet('color: red; font-family:Times New Roman')
					self.status_label.setText(str("Cant downloadFile, Try open instead"))
					return
			else:
				self.ftpClient.directory_return()
				self.ftpClient.directory_print()
				self.refreshRemote()
		self.setStatus()
	def updateServerDirectoryList(self):
		
		
		try:
			self.remoteDir_tableWidget.setRowCount(0)
			
			# set column count
			self.remoteDir_tableWidget.setColumnCount(4)
			
			# Set Row Count:
			self.remoteDir_tableWidget.setRowCount(len(self.ftpClient.ListInDir)+1)
			# Default:
			self.remoteDir_tableWidget.setItem(0,0, QtWidgets.QTableWidgetItem(".."))
			#self.remoteDir_tableWidget.setColumnWidth(0, 230)
			header = self.remoteDir_tableWidget.horizontalHeader()
			header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
			header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
			header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
			
			row = 1
			col = 0
			for item in self.ftpClient.ListInDir:
				#print(item)
				for fileProperty in item:
					fileTypeIco = None
					if col==0:
						if item[3].find('x') is -1:
							tempFilename = fileProperty.lower()
							if tempFilename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
								fileTypeIco = "assets/image.ico"
							elif tempFilename.endswith(('.mp4', '.wmv', '.mkv', '.avi')):
								fileTypeIco = "assets/video.ico"
							else:
								fileTypeIco = "assets/file.ico"
						else:
							fileTypeIco = "assets/folder.ico"
					
					tempItem = QtWidgets.QTableWidgetItem(QtGui.QIcon(QtGui.QPixmap(fileTypeIco)), fileProperty)
					self.remoteDir_tableWidget.setItem(row,col, tempItem)
					col = col+1
				row = row+1
				col = 0
			self.remoteDir_tableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Name"))
			self.remoteDir_tableWidget.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Size"))
			self.remoteDir_tableWidget.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem("Last Modified"))
			self.remoteDir_tableWidget.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem("Permissions"))
			self.remoteDir_tableWidget.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
			#self.remoteDir_tableWidget.setShowGrid(False)
			#self.updateServerDirectoryList()
		
			
		except:
			self.status_label.setStyleSheet('color: red; font-family:Times New Roman')
			self.status_label.setText(str("Unable to update Server Directory."))
	def refreshRemote(self):
		if self.ftpClient.IsConnected:
			self.ftpClient.getDirList()
			self.updateServerDirectoryList()
	
	def refreshLocal(self):
		self.populateLocalDir()
		
	def updateStatus(self):
		time.sleep(2)
		self.status_label.setStyleSheet('color: blue; font-family:Times New Roman')
		self.status_label.setText(str("Online"))
	def quit(self):
		if self.ftpClient.IsConnected:
			self.ftpClient.logout()
			self.Quit_pushButton.setEnabled(False)
			self.btn_refreshRemoteDir.setEnabled(False)
			self.remoteDir_tableWidget.clear()
			self.remoteDir_tableWidget.setEnabled(False)
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
