import sys
from threading import Thread
#from pyqtconsole.console import PythonConsole
from PyQt5 import QtSvg
from PyQt5.QtCore import pyqtSlot, QProcess, Qt, QRect
from PyQt5.QtGui import QKeySequence, QTextCursor, QPainter, QColor, QTextFormat
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QFileDialog, QAction, QPlainTextEdit, QGridLayout, QDialog, QLabel, QMainWindow, QMdiArea, QMdiSubWindow, QShortcut, QTabWidget
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
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create parts
        self.view = QtSvg.QSvgWidget("ichimatsu.svg")
        self.bkg = QtSvg.QSvgWidget("ichimatsu.svg")

        self.button_save = QPushButton("Save", self)
        self.button_save.setToolTip("Save the current graph")

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(self.bkg, 1, 1)
        self.grid.addWidget(self.view, 1, 1)
        self.grid.addWidget(self.button_save, 2, 1)
        self.setLayout(self.grid)

        self.show()
