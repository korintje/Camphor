import sys
from threading import Thread
#from pyqtconsole.console import PythonConsole
from PyQt5 import QtSvg
from PyQt5.QtCore import pyqtSlot, QProcess, Qt, QRect
from PyQt5.QtGui import QKeySequence, QTextCursor, QPainter, QColor, QTextFormat
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QFileDialog, QAction, QPlainTextEdit, QGridLayout, QDialog, QLabel, QMainWindow, QMdiArea, QMdiSubWindow, QShortcut, QTabWidget
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
import syntax

class OutputWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.title = "Console Output"
        self.left = 10
        self.top = 10
        self.width = 960
        self.height = 240

        self.initUI()

    def initUI(self):
        # Set the title and window size
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create parts
        self.stdout = QTextEdit(self)
        self.stdout.setReadOnly(True)
        self.stdout.setUndoRedoEnabled( False )
        self.stdout.setStyleSheet("background-color: rgb(36, 36, 36);" "color: rgb(48, 255, 48)")
        self.stdout.cursor = self.stdout.textCursor()

        self.grid = QGridLayout()
        #self.grid.addWidget(self.tabs)
        #self.grid.setSpacing(10)
        self.grid.addWidget(self.stdout, 2,0,1,1)
        #self.grid.addWidget(self.errout, 2,1,1,1)
        self.setLayout(self.grid)

        self.show()
