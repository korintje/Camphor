import sys
from threading import Thread
#from pyqtconsole.console import PythonConsole
from PyQt5 import QtSvg
from PyQt5.QtCore import pyqtSlot, QProcess, Qt, QRect, QSize
from PyQt5.QtGui import QTextCursor, QPainter, QColor, QTextFormat
from PyQt5.QtWidgets import QApplication, QWidget, QSizePolicy, QFrame, QPushButton, QVBoxLayout, QTextEdit, QFileDialog, QAction, QPlainTextEdit, QGridLayout, QDialog, QLabel, QMainWindow, QMdiArea, QMdiSubWindow, QShortcut, QTabWidget
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO

class ViewerWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.title = "Image View"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 640

        self.initUI()

    def initUI(self):
        # Set the title and window size
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)

        # Create parts
        #self.view = QtSvg.QSvgWidget("ichimatsu.svg")
        #self.view = SVGView()
        #policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        #policy.setHeightForWidth(True)
        #self.view.setSizePolicy(policy)
        #self.view.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #self.view.heightForWidth(10)
        #self.bkg = QtSvg.QSvgWidget("ichimatsu.svg")

        """

        self.button_save = QPushButton("Save", self)
        self.button_save.setToolTip("Save the current graph")

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        #self.grid.addWidget(self.bkg, 1, 1)
        #self.grid.addWidget(self.view, 1, 1)
        self.grid.addWidget(self.button_save, 2, 1)
        self.setLayout(self.grid)
        """
        layout = QVBoxLayout()
        self.custom_widget = CustomWidget()
        layout.addWidget(self.custom_widget)
        self.setLayout(layout)

        self.show()

class CustomWidget(QFrame):
    def __init__(self, parent=None):
        #super().__init__()
        QFrame.__init__(self, parent)

        # Give the frame a border so that we can see it.
        self.setFrameStyle(1)

        self.view = QtSvg.QSvgWidget("ichimatsu.svg")
        self.bkg = QtSvg.QSvgWidget("ichimatsu.svg")
        #layout = QVBoxLayout()
        layout = QGridLayout()
        #self.grid.setSpacing(10)
        layout.addWidget(self.bkg, 1, 1)
        layout.addWidget(self.view, 1, 1)
        #layout.addWidget(self.button_save, 2, 1)
        #self.setLayout(self.grid)
        #self.label = QLabel('Test')

        #layout.addWidget(self.view)
        self.setLayout(layout)

    def resizeEvent(self, event):
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        new_size = QSize(10, 10)
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.resize(new_size)

class SVGView(QtSvg.QSvgWidget):

    def __init__(self):
        super().__init__()
        policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

    def heightForWidth(self, width):
        return width
