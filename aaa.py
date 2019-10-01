import sys
from PyQt5 import QtSvg
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QFileDialog, QAction, QPlainTextEdit, QGridLayout, QDialog, QLabel, QMainWindow
from PyQt5.QtCore import pyqtSlot
import subprocess
from PyQt5.QtGui import QIcon
import xml.etree.ElementTree as ET

#import subprocess
import pickle

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MultiWindows(QMainWindow):

    def __init__(self):
        super().__init__()
        self.__windows = []

    def addwindow(self, window):
        self.__windows.append(window)

    def show(self):
        for current_child_window in self.__windows:
             current_child_window.exec_() # probably show will do the same trick

class PlanetApp(QDialog):
    def __init__(self, parent, planet):
       QDialog.__init__(self, parent)
       # do cool stuff here

class AnimalApp(QDialog):
    def __init__(self, parent, animal):
       QDialog.__init__(self, parent)
       # do cool stuff here

if __name__=="__main__":
    import sys # really need this here??

    app = QApplication(sys.argv)

    jupiter = PlanetApp(None, "jupiter")
    venus = PlanetApp(None, "venus")
    windows = MultiWindows()
    windows.addwindow(jupiter)
    windows.addwindow(venus)

    windows.show()
    app.exec_()
