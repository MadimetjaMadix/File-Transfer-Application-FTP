import os
import sys
import time
import socket
import random
import string
import traceback
import threading
from threading import Thread

from FTP_Client import FTPClient
from FTP_Client import DownloadProgres


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileSystemModel, QTreeView, QWidget, QHBoxLayout, QApplication
from ClientUI import Ui_ClientUI

class actionSignals(QtCore.QObject):
	'''
	Defines the signals available from a running worker thread.
	Supported signals are:
	finished -> No data
	error -> tuple` (exctype, value, traceback.format_exc() )
	result-> object` data returned from processing, anything
	'''
	finished = QtCore.pyqtSignal()
	error = QtCore.pyqtSignal(tuple)
	fileProgress = QtCore.pyqtSignal()


class actionHandler(QtCore.QRunnable):
	# Thread to handle functions
	def __init__(self, function, *args, **kwargs):
		super(actionHandler, self).__init__()
		self.runFunction = function
		self.args = args
		self.signals = actionSignals()
		kwargs['progress_callback'] = self.signals.fileProgress
		self.kwargs = kwargs
		
	@QtCore.pyqtSlot()
	def run(self):
		
		try:
			self.runFunction(*self.args, **self.kwargs)
		except:
			traceback.print_exc()
			exctype, value = sys.exc_info()[:2]
			self.signals.error.emit((exctype, value, traceback.format_exc()))
		
		finally:
			self.signals.finished.emit()  # Done


class clientUI_Interface(Ui_ClientUI):
	def __init__(self, ftpClientUIMain, ftpClient, homeDir):
			Ui_ClientUI.__init__(self)
			self.setupUi(ftpClientUIMain)
			self.ftpClient = ftpClient
			self.homeDir = homeDir
			self.localDir_treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
			self.localDir_treeView.customContextMenuRequested.connect(self.localMenu)
			
			self.remoteDir_tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
			self.remoteDir_tableWidget.customContextMenuRequested.connect(self.remoteMenu)
			
			#-----------------remote-------------------
			self.progressBar.setValue(0)
			self.progressBar.hide()
			self.Back_pushButton.setEnabled(False)
			self.Quit_pushButton.setEnabled(False)
			self.btn_refreshRemoteDir.setEnabled(False)
			self.remoteDir_tableWidget.setEnabled(False)
			self.dirName_lineEdit.setEnabled(False)
			self.btn_createDir.setEnabled(False)
			self.btn_Cancell_createDir.setEnabled(False)
			self.updateServerDirectoryList()
			#-----------------Local-------------------
			self.populateLocalDir()
			self.threadpool = QtCore.QThreadPool()
			#---------------------------------
			self.connect_pushButton.clicked.connect(self.connectToServer)
			self.Quit_pushButton.clicked.connect(self.quit)
			self.btn_refreshRemoteDir.clicked.connect(self.refreshRemote)
			self.btn_RefreshLocalDir.clicked.connect(self.refreshLocal)
			self.btn_createDir.clicked.connect(self.createDir)
			self.btn_Cancell_createDir.clicked.connect(self.disableFolderEdit)
			self.Back_pushButton.clicked.connect(self.directoryReturn)
			
	def setSatus(self, isError,status):
		self.ftpClient.isError = isError
		self.ftpClient.server_response = status
		self.dispStatus()

		
	def dispStatus(self):
		if self.ftpClient.isError:
			self.status_label.setStyleSheet('color: red; font-family:Times New Roman')
		else:
			self.status_label.setStyleSheet('color: blue; font-family:Times New Roman; font-size: 11pt')
			
		self.status_label.setText(str(self.ftpClient.server_response))
		
	def connectToServer(self):
		if not self.ftpClient.IsConnected:
			self.ftpClient.initializeFTPConnection(str(self.lineEdit_host.text()))
			self.dispStatus()
		self.loginToServer()
		if self.ftpClient.IsValidUser:
			self.Quit_pushButton.setEnabled(True)
			self.connect_pushButton.setEnabled(False)
			self.connect_pushButton.setText("Connect")
			self.Back_pushButton.setEnabled(True)
			self.btn_refreshRemoteDir.setEnabled(True)
			self.remoteDir_tableWidget.setEnabled(True)
			self.refreshRemote()
			self.conStatus.setStyleSheet('color: blue; font-family:Times New Roman; font-size: 11pt')
			self.conStatus.setText("Online : ")
			self.dispStatus()
		
	def loginToServer(self):
		if self.ftpClient.IsConnected:
			self.connect_pushButton.setText("Login")
			username = str(self.lineEdit_username.text())
			password = str(self.lineEdit_Password.text())
			self.ftpClient.login(username, password)
			self.dispStatus()
			
	def populateLocalDir(self):
		
		self.localModel = QFileSystemModel()
		self.localModel.setRootPath(QtCore.QDir.rootPath())
		self.localDir_treeView.setModel(self.localModel)
		self.localDir_treeView.setRootIndex(self.localModel.index(str(self.homeDir)))
		self.localDir_treeView.setSortingEnabled(True)
		
	def localMenu(self):
		local_menu = QtWidgets.QMenu()
		fileUpload = local_menu.addAction("Upload")
		fileUpload.triggered.connect(self.uploadFile)
		cursor = QtGui.QCursor()	#privide a cursor location
		local_menu.exec_(cursor.pos())	# pass it to the menu executor
		
	def uploadFile(self):
		local_index = self.localDir_treeView.currentIndex()
		filename = self.localModel.fileName(local_index)
		filepath = self.localModel.filePath(local_index)
		
		#self.ftpClient.upload_file(filename)
		
		self.ftpClient.upLoadList.append(filename)
		uploadThread = actionHandler(self.ftpClient.upload_file, filename, filepath)
						
		uploadThread.signals.finished.connect(self.uploadThreadComplete)
		uploadThread.signals.error.connect(self.uploadFailed)
		uploadThread.signals.fileProgress.connect(self.displayUploadProgBar)
						
		self.threadpool.start(uploadThread)
		
		msg = "Upload file : " + filename
		self.setSatus(False,msg)
		self.dispStatus()
		
	def uploadFailed(self):
		print("Upload Failed")
		
	def uploadThreadComplete(self):
		self.setSatus(False,"Done Uploading")
		self.dispStatus()
		self.progressBar.hide()
		self.up_downLoadlabel.setText("")
		self.progressBar.setEnabled(False)
		self.Back_pushButton.setEnabled(True)
		self.btn_refreshRemoteDir.setEnabled(True)
		self.remoteDir_tableWidget.setEnabled(True)
		self.refreshRemote()
		
	def displayUploadProgBar(self):#, filename)
		
		if len(self.ftpClient.upLoadList) is not 0:
			self.progressBar.show()
			self.progressBar.setEnabled(True)
			self.up_downLoadlabel.setText("Uploading file")
			self.progressBar.setValue(self.ftpClient.getProgressVal())
		return
		
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
						self.dispStatus()
						self.refreshRemote()
					else:
						path = self.addPath(filename)
						self.ftpClient.file_delete(path)
						self.dispStatus()
						self.refreshRemote()
				except:
					self.setSatus(True,"Cant delete File")
					self.dispStatus()
					return
					
	def enableFolderEdit(self):
		self.dirName_lineEdit.setEnabled(True)
		self.btn_createDir.setEnabled(True)
		self.label_foldername.setEnabled(True)
		self.btn_Cancell_createDir.setEnabled(True)
		self.Back_pushButton.setEnabled(False)
		self.btn_refreshRemoteDir.setEnabled(False)
		self.remoteDir_tableWidget.setEnabled(False)
		
	def disableFolderEdit(self):
		self.btn_Cancell_createDir.setEnabled(False)
		self.dirName_lineEdit.setEnabled(False)
		self.label_foldername.setEnabled(False)
		self.btn_createDir.setEnabled(False)
		self.Back_pushButton.setEnabled(True)
		self.btn_refreshRemoteDir.setEnabled(True)
		self.remoteDir_tableWidget.setEnabled(True)
		
	def createDir(self):
		self.dirName_lineEdit.setFocus()
		directoryName = str(self.dirName_lineEdit.text())
		self.dirName_lineEdit.clear()
		self.ftpClient.directory_create(directoryName)
		self.disableFolderEdit()
		self.dispStatus()
		self.refreshRemote()
		return

	def addPath(self,filename):
		self.ftpClient.directory_print()
		print(self.ftpClient.serverDir)
		self.ftpClient.serverDir = self.ftpClient.serverDir.replace('\r\n', '')
		s = '\\'
		path = self.ftpClient.serverDir + s + filename
		path = [self.ftpClient.serverDir,str(filename)]
		path = '\\'.join(path)
		return path
	def openFolder(self):
		for currentQTableWidgetRow in self.remoteDir_tableWidget.selectionModel().selectedRows():
			if currentQTableWidgetRow.row()!=0:
				print(currentQTableWidgetRow.row())
				try:
					filename = self.remoteDir_tableWidget.item(currentQTableWidgetRow.row(), 0).text()
					permission = self.remoteDir_tableWidget.item(currentQTableWidgetRow.row(), 3).text()
					if permission.find('d') is not -1:
						path = self.addPath(filename)
						print('path :',path)
						self.ftpClient.directory_change(path)
						self.dispStatus()
						self.refreshRemote()
					else:
						self.setSatus(True,"Cant open file, Download instead")
						self.dispStatus()
						
				except:
					self.setSatus(True,"Cant open file, Download instead")
					self.dispStatus()
					
			elif currentQTableWidgetRow.row()==0:
				self.directoryReturn()
			else:
				self.updateCurrentDir()
				self.ftpClient.directory_print()
				self.dispStatus()
				self.refreshRemote()
				
	def directoryReturn(self):
		self.ftpClient.directory_return()
		self.ftpClient.directory_print()
		self.dispStatus()
		self.refreshRemote()
		
	def downloadFile(self):
		for currentQTableWidgetRow in self.remoteDir_tableWidget.selectionModel().selectedRows():
			if currentQTableWidgetRow.row()!=0:
				filename = self.remoteDir_tableWidget.item(currentQTableWidgetRow.row(), 0).text()
				permission = self.remoteDir_tableWidget.item(currentQTableWidgetRow.row(), 3).text()
				if permission.find('d') is -1:
					try:
						#saveFileInDirectory = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Save File In Directory", currentDirectory,\
						#QtWidgets.QFileDialog.ShowDirsOnly))
						
						self.ftpClient.downloadList.append(filename)
						self.callDownloadFn()
						
						downloadThread = actionHandler(self.ftpClient.download_file,filename)
						
						downloadThread.signals.finished.connect(self.downloadThreadComplete)
						downloadThread.signals.error.connect(self.downloadFailed)
						downloadThread.signals.fileProgress.connect(self.displayDownloadProgBar)
						
						self.threadpool.start(downloadThread)
						
					except:
						
						print("Error creating download Thread")
				else:
					self.setSatus(True,"Cant downloadFile, Try open instead")
					self.dispStatus()
					
		self.dispStatus()
		
	def callDownloadFn(self):
		#progressThread = actionHandler(self.displayDownloadProgBar())
		#self.threadpool.start(downloadThread)
		self.setSatus(False,"Downloading ...")
		self.dispStatus()
		self.Back_pushButton.setEnabled(False)
		self.btn_refreshRemoteDir.setEnabled(False)
		self.remoteDir_tableWidget.setEnabled(False)
		
		#self.ftpClient.download_file(fileName, progress_callback )
		
		

	def downloadFailed(self):
		print("download Failed")
		
	def downloadThreadComplete(self):
		self.setSatus(False,"Done Downloading")
		self.dispStatus()
		self.refreshRemote()
		self.progressBar.hide()
		self.up_downLoadlabel.setText("")
		self.progressBar.setEnabled(False)
		self.Back_pushButton.setEnabled(True)
		self.btn_refreshRemoteDir.setEnabled(True)
		self.remoteDir_tableWidget.setEnabled(True)
		
	def displayDownloadProgBar(self):#, filename)
		
		if len(self.ftpClient.downloadList) is not 0:
			self.progressBar.show()
			self.progressBar.setEnabled(True)
			self.up_downLoadlabel.setText("Downloading file")
			self.progressBar.setValue(self.ftpClient.getProgressVal())
		return
		
	def updateCurrentDir(self):
		self.ftpClient.directory_print()
		self.remoteDir_lineEdit.setText(str(self.ftpClient.serverDir))
	def updateServerDirectoryList(self):
		
		try:
			self.remoteDir_tableWidget.setRowCount(0)
			
			# set column count
			self.remoteDir_tableWidget.setColumnCount(4)
			
			# Set Row Count:
			self.remoteDir_tableWidget.setRowCount(len(self.ftpClient.ListInDir)+1)
			# Default:
			self.remoteDir_tableWidget.setItem(0,0, QtWidgets.QTableWidgetItem(".."))
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
			
			
		except:
			self.setSatus(True,"Unable to update Server Directory.")
			self.dispStatus()
			
	def refreshRemote(self):
		if self.ftpClient.IsConnected:
			self.ftpClient.getDirList()
			self.updateServerDirectoryList()
			self.updateCurrentDir()
			#self.setSatus(False,"Remote Directory refreshed")
			self.dispStatus()
	
	def refreshLocal(self):
		self.populateLocalDir()
		
		
	def updateStatus(self):
		time.sleep(1)
		if self.ftpClient.IsConnected:
			self.status_label.setStyleSheet('color: blue; font-family:Times New Roman; font-size: 11pt')
			self.status_label.setText("...")
			
	def quit(self):
		if self.ftpClient.IsConnected:
			self.ftpClient.logout()
			self.Quit_pushButton.setEnabled(False)
			self.btn_refreshRemoteDir.setEnabled(False)
			self.remoteDir_lineEdit.setText("")
			self.remoteDir_tableWidget.clear()
			self.remoteDir_tableWidget.setEnabled(False)
			self.connect_pushButton.setEnabled(True)
			self.conStatus.setStyleSheet('color: red; font-family:Times New Roman; font-size: 11pt')
			self.conStatus.setText("Offline :")
			self.status_label.setText('')
			self.Back_pushButton.setEnabled(False)
			
if __name__ == '__main__':

	app = QtWidgets.QApplication(sys.argv)
	ftpClientUIMain = QtWidgets.QMainWindow()
	ftpClient = FTPClient()
	homeDir = os.getcwd()
	prog = clientUI_Interface(ftpClientUIMain, ftpClient, homeDir)
	ftpClientUIMain.show()
	sys.exit(app.exec_())
