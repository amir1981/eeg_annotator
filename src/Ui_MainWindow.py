# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '1.ui'
#
# Created: Sun Aug 31 16:39:49 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.plotWidget = EditPlotWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotWidget.sizePolicy().hasHeightForWidth())
        self.plotWidget.setSizePolicy(sizePolicy)
        self.plotWidget.setObjectName(_fromUtf8("plotWidget"))
        self.verticalLayout.addWidget(self.plotWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName(_fromUtf8("menuAbout"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtGui.QDockWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidget.sizePolicy().hasHeightForWidth())
        self.dockWidget.setSizePolicy(sizePolicy)
        self.dockWidget.setMinimumSize(QtCore.QSize(177, 38))
        self.dockWidget.setMaximumSize(QtCore.QSize(177, 524287))
        self.dockWidget.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.edfListWidget = QtGui.QListWidget(self.dockWidgetContents)
        self.edfListWidget.setGeometry(QtCore.QRect(30, 40, 141, 301))
        self.edfListWidget.setObjectName(_fromUtf8("edfListWidget"))
        self.amplitudeSpinBox = QtGui.QDoubleSpinBox(self.dockWidgetContents)
        self.amplitudeSpinBox.setGeometry(QtCore.QRect(110, 370, 62, 22))
        self.amplitudeSpinBox.setObjectName(_fromUtf8("amplitudeSpinBox"))
        self.timeSpinBox = QtGui.QDoubleSpinBox(self.dockWidgetContents)
        self.timeSpinBox.setGeometry(QtCore.QRect(110, 400, 62, 22))
        self.timeSpinBox.setObjectName(_fromUtf8("timeSpinBox"))
        self.showLabelButton = QtGui.QPushButton(self.dockWidgetContents)
        self.showLabelButton.setEnabled(False)
        self.showLabelButton.setGeometry(QtCore.QRect(30, 430, 141, 25))
        self.showLabelButton.setCheckable(True)
        self.showLabelButton.setObjectName(_fromUtf8("showLabelButton"))
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setGeometry(QtCore.QRect(30, 20, 57, 15))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.dockWidgetContents)
        self.label_2.setGeometry(QtCore.QRect(30, 370, 71, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.dockWidgetContents)
        self.label_3.setGeometry(QtCore.QRect(30, 400, 71, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.markFinishButton = QtGui.QPushButton(self.dockWidgetContents)
        self.markFinishButton.setGeometry(QtCore.QRect(30, 490, 141, 25))
        self.markFinishButton.setObjectName(_fromUtf8("markFinishButton"))
        self.line = QtGui.QFrame(self.dockWidgetContents)
        self.line.setGeometry(QtCore.QRect(0, 470, 201, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.line_2 = QtGui.QFrame(self.dockWidgetContents)
        self.line_2.setGeometry(QtCore.QRect(-10, 340, 201, 20))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionPrint = QtGui.QAction(MainWindow)
        self.actionPrint.setObjectName(_fromUtf8("actionPrint"))
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionPrint)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuAbout.setTitle(_translate("MainWindow", "About ", None))
        self.dockWidget.setWindowTitle(_translate("MainWindow", "Control Panel", None))
        self.showLabelButton.setText(_translate("MainWindow", "Show Class Names", None))
        self.label.setText(_translate("MainWindow", "Files", None))
        self.label_2.setText(_translate("MainWindow", "Amp. scale", None))
        self.label_3.setText(_translate("MainWindow", "Time scale", None))
        self.markFinishButton.setText(_translate("MainWindow", "Mark File as Finished", None))
        self.actionNew.setText(_translate("MainWindow", "New ", None))
        self.actionOpen.setText(_translate("MainWindow", "Open ", None))
        self.actionExit.setText(_translate("MainWindow", "Exit ", None))
        self.actionPrint.setText(_translate("MainWindow", "Print", None))

from EditPlotWidget import EditPlotWidget
