# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ClientUI.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ClientUI(object):
    def setupUi(self, ClientUI):
        ClientUI.setObjectName("ClientUI")
        ClientUI.resize(1072, 607)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        ClientUI.setFont(font)
        self.centralwidget = QtWidgets.QWidget(ClientUI)
        self.centralwidget.setObjectName("centralwidget")
        self.connect_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.connect_pushButton.setGeometry(QtCore.QRect(900, 10, 81, 21))
        self.connect_pushButton.setObjectName("connect_pushButton")
        self.lineEdit_host = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_host.setGeometry(QtCore.QRect(60, 10, 171, 21))
        self.lineEdit_host.setObjectName("lineEdit_host")
        self.lineEdit_Password = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_Password.setGeometry(QtCore.QRect(620, 10, 113, 21))
        self.lineEdit_Password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_Password.setObjectName("lineEdit_Password")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 47, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(280, 10, 81, 20))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(540, 10, 71, 20))
        self.label_3.setObjectName("label_3")
        self.lineEdit_Port = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_Port.setGeometry(QtCore.QRect(832, 10, 61, 21))
        self.lineEdit_Port.setObjectName("lineEdit_Port")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(790, 10, 47, 21))
        self.label_4.setObjectName("label_4")
        self.status_label = QtWidgets.QLabel(self.centralwidget)
        self.status_label.setGeometry(QtCore.QRect(10, 50, 521, 21))
        self.status_label.setText("")
        self.status_label.setObjectName("status_label")
        self.localDir_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.localDir_lineEdit.setGeometry(QtCore.QRect(10, 80, 521, 21))
        self.localDir_lineEdit.setObjectName("localDir_lineEdit")
        self.remoteDir_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.remoteDir_lineEdit.setGeometry(QtCore.QRect(540, 80, 521, 21))
        self.remoteDir_lineEdit.setObjectName("remoteDir_lineEdit")
        self.lineEdit_username = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_username.setGeometry(QtCore.QRect(360, 10, 171, 21))
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(False)
        self.progressBar.setGeometry(QtCore.QRect(540, 50, 521, 23))
        self.progressBar.setAutoFillBackground(False)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.Quit_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.Quit_pushButton.setGeometry(QtCore.QRect(990, 10, 71, 21))
        self.Quit_pushButton.setObjectName("Quit_pushButton")
        self.localDir_treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.localDir_treeWidget.setGeometry(QtCore.QRect(540, 110, 521, 451))
        self.localDir_treeWidget.setObjectName("localDir_treeWidget")
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.localDir_treeWidget.headerItem().setFont(0, font)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.localDir_treeWidget.headerItem().setFont(1, font)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.localDir_treeWidget.headerItem().setFont(2, font)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.localDir_treeWidget.headerItem().setFont(3, font)
        self.localDir_treeView = QtWidgets.QTreeView(self.centralwidget)
        self.localDir_treeView.setGeometry(QtCore.QRect(10, 110, 521, 451))
        self.localDir_treeView.setObjectName("localDir_treeView")
        ClientUI.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ClientUI)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1072, 21))
        self.menubar.setObjectName("menubar")
        ClientUI.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ClientUI)
        self.statusbar.setObjectName("statusbar")
        ClientUI.setStatusBar(self.statusbar)

        self.retranslateUi(ClientUI)
        QtCore.QMetaObject.connectSlotsByName(ClientUI)

    def retranslateUi(self, ClientUI):
        _translate = QtCore.QCoreApplication.translate
        ClientUI.setWindowTitle(_translate("ClientUI", "MainWindow"))
        self.connect_pushButton.setText(_translate("ClientUI", "Connect"))
        self.label.setText(_translate("ClientUI", "Host :"))
        self.label_2.setText(_translate("ClientUI", "Username :"))
        self.label_3.setText(_translate("ClientUI", "Password :"))
        self.label_4.setText(_translate("ClientUI", "Port :"))
        self.Quit_pushButton.setText(_translate("ClientUI", "Quit"))
        self.localDir_treeWidget.headerItem().setText(0, _translate("ClientUI", "Filename"))
        self.localDir_treeWidget.headerItem().setText(1, _translate("ClientUI", "Lastmodified"))
        self.localDir_treeWidget.headerItem().setText(2, _translate("ClientUI", "Filetype"))
        self.localDir_treeWidget.headerItem().setText(3, _translate("ClientUI", "Filesize"))

