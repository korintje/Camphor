import sys
from PyQt5 import QtSvg
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QFileDialog, QAction, QPlainTextEdit, QGridLayout, QDialog, QLabel
from PyQt5.QtCore import pyqtSlot
import subprocess
from PyQt5.QtGui import QIcon
import xml.etree.ElementTree as ET

#import subprocess
import pickle

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = "test-program"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 640
        self.initUI()

    def initUI(self):
        # Set the title and window size
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #Create ImageViewer
        self.imageviewer = ImageViewer()
        self.imageviewer.show()

        # Create parts
        self.edit = QPlainTextEdit(self)
        self.edit.setPlainText("Open an existing .svg file or write a script")

        #self.view = QtSvg.QSvgWidget("test3.svg")

        self.button_exec = QPushButton("Update", self)
        self.button_exec.setToolTip("Update the graph")
        self.button_exec.clicked.connect(lambda: self.on_click(self.edit.toPlainText()))

        self.button_read = QPushButton("Read", self)
        self.button_read.setToolTip("Read .svg file")
        self.button_read.clicked.connect(lambda: self.read_svg())

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(self.edit, 1, 1)
        self.grid.addWidget(self.button_exec, 2, 1)
        self.grid.addWidget(self.button_read, 2, 2)
        self.grid.addWidget(self.view, 3, 1)
        self.setLayout(self.grid)

        self.show()

    @pyqtSlot()
    def on_click(self, script):
        #print(script)
        #subprocess.check_output(["python", script])
        exec(script)
        #with open("temp.svg", "rb") as f:
        self.imageviewer.svg_load("temp.svg")
            #fid = pickle.load(f)
        #fid = exec(script)
        #print(fid)
        #self.view.load(fid)
        #print("LOADED")

    @pyqtSlot()
    def read_svg(self):
        print("READ")
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        # fname[0]は選択したファイルのパス（ファイル名を含む）
        if fname[0]:
            # テキストエディタにファイル内容書き込み
            svg_tree = ET.parse(fname[0])
            root = svg_tree.getroot()
            for metadata in root.iter("{http://www.w3.org/2000/svg}metadata"):
                print(metadata.tag)
                for metadatum in metadata:
                    print(metadatum.tag)
                    if metadatum.tag == "{https://korintje.com}script":
                        print(metadatum.text)
                        self.edit.setPlainText(metadatum.text)
                break

class ImageViewer(QWidget):

    def __init__(self, parent=None):
        #super().__init__()
        self.w = QDialog(parent)
        label = QLabel()
        label.setText("subwindow")

        self.view = QtSvg.QSvgWidget("test3.svg")

        #self.grid = QGridLayout()
        #self.grid.setSpacing(10)
        #self.grid.addWidget(self.view, 3, 1)
        #self.setLayout(self.grid)

    def show(self):
        self.w.exec_()

    def svg_load(self, filename):
        self.view.load(filename)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
