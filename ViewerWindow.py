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
        self.setWindowTitle(self.title)

        self.view = CustomWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.show()


class CustomWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__()
        #QFrame.__init__(self, parent)
        self.svg_view = QtSvg.QSvgWidget("ichimatsu.svg")
        self.svg_bkg = QtSvg.QSvgWidget("ichimatsu.svg")

        self.original_size_view = self.getDefaultSize("ichimatsu.svg")
        print(self.original_size_view)
        self.original_size_bkg = self.getDefaultSize("ichimatsu.svg")

        layout = QGridLayout()
        layout.addWidget(self.svg_bkg, 1, 1)
        layout.addWidget(self.svg_view, 1, 1)
        self.setLayout(layout)

    def loadSVGview(self, filename):
        self.svg_view.load(filename)
        self.original_size_view = self.getDefaultSize(filename)

    def loadSVGbkg(self, filename):
        self.svg_bkg.load(filename)
        self.bkg_size_view = self.getDefaultSize(filename)

    def getDefaultSize(self, filename):
        renderer =  QtSvg.QSvgRenderer(filename)
        return renderer.defaultSize()

    def resizeEvent(self, event):
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        #new_size = QSize(10, 10)
        new_size = self.original_size_view
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.resize(new_size)
