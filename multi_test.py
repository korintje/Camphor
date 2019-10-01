import sys
from PyQt5 import QtSvg
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QFileDialog, QAction, QPlainTextEdit, QGridLayout, QDialog, QLabel, QMainWindow, QMdiArea, QMdiSubWindow
import xml.etree.ElementTree as ET


print("READ")
    # テキストエディタにファイル内容書き込み
svg_tree = ET.parse("test6.svg")
root = svg_tree.getroot()
#for g in root.iter("{http://www.w3.org/2000/svg}g"):
for g in root.findall("{http://www.w3.org/2000/svg}g"):
    if "{http://www.inkscape.org/namespaces/inkscape}groupmode" in g.attrib and g.attrib["{http://www.inkscape.org/namespaces/inkscape}groupmode"] == "layer":
        if "{http://www.inkscape.org/namespaces/inkscape}label" in g.attrib and g.attrib["{http://www.inkscape.org/namespaces/inkscape}label"] == "Layer_mpl":
            print(g.tag)
            print(g.attrib)
            print("FOUND")
            root.remove(g)
            print("REMOVED")
        else:
            print(g.tag)
            print(g.attrib)
            print("other layers")
    else:
        print("404 NOT FOUND")


print("2nd")

for g in root.findall("{http://www.w3.org/2000/svg}g"):
    if "{http://www.inkscape.org/namespaces/inkscape}groupmode" in g.attrib and g.attrib["{http://www.inkscape.org/namespaces/inkscape}groupmode"] == "layer":
        if "{http://www.inkscape.org/namespaces/inkscape}label" in g.attrib and g.attrib["{http://www.inkscape.org/namespaces/inkscape}label"] == "Layer_mpl":
            print(g.tag)
            print(g.attrib)
            print("FOUND")
            root.remove(g)
            print("REMOVED")
        else:
            print(g.tag)
            print(g.attrib)
            print("other layers")
    else:
        print("404 NOT FOUND")
