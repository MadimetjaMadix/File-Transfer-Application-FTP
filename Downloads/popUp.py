# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'popUp.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CreateDirectoryWindow(object):
    def setupUi(self, CreateDirectoryWindow):
        CreateDirectoryWindow.setObjectName("CreateDirectoryWindow")
        CreateDirectoryWindow.resize(362, 129)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CreateDirectoryWindow.sizePolicy().hasHeightForWidth())
        CreateDirectoryWindow.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        CreateDirectoryWindow.setFont(font)
        CreateDirectoryWindow.setFocusPolicy(QtCore.Qt.StrongFocus)
        CreateDirectoryWindow.setWindowOpacity(20.0)
        self.createFolder_pushButton = QtWidgets.QPushButton(CreateDirectoryWindow)
        self.createFolder_pushButton.setGeometry(QtCore.QRect(130, 70, 75, 23))
        self.createFolder_pushButton.setObjectName("createFolder_pushButton")
        self.Foldername_lineEdit = QtWidgets.QLineEdit(CreateDirectoryWindow)
        self.Foldername_lineEdit.setGeometry(QtCore.QRect(30, 40, 281, 20))
        self.Foldername_lineEdit.setObjectName("Foldername_lineEdit")
        self.label = QtWidgets.QLabel(CreateDirectoryWindow)
        self.label.setGeometry(QtCore.QRect(70, 10, 211, 20))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.retranslateUi(CreateDirectoryWindow)
        QtCore.QMetaObject.connectSlotsByName(CreateDirectoryWindow)

    def retranslateUi(self, CreateDirectoryWindow):
        _translate = QtCore.QCoreApplication.translate
        CreateDirectoryWindow.setWindowTitle(_translate("CreateDirectoryWindow", "Create directory"))
        self.createFolder_pushButton.setText(_translate("CreateDirectoryWindow", "Create"))
        self.label.setText(_translate("CreateDirectoryWindow", "Enter Folder Name"))

