import sys
from threading import Thread
from PyQt5 import QtSvg
from PyQt5.QtCore import pyqtSlot, QProcess, Qt, QRect
from PyQt5.QtGui import QKeySequence, QTextCursor, QPainter, QColor, QTextFormat
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QFileDialog, QAction, QPlainTextEdit, QGridLayout, QDialog, QLabel, QMainWindow, QMdiArea, QMdiSubWindow, QShortcut, QTabWidget
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
import syntax

from ViewerWindow import ViewerWindow
from ScriptWindow import ScriptWindow
from OutputWindow import OutputWindow

def register_all_namespaces(filename):
    namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])

class MainWindow(QMainWindow):
    count = 0
    linecount = 0
    maxLine = 100

    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.item0 = BytesIO()

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        bar = self.menuBar()

        file = bar.addMenu("File")
        file.addAction("New")
        file.addAction("cascade")
        file.addAction("Tiled")
        file.triggered[QAction].connect(self.windowaction)
        self.setWindowTitle("Camphor")

        MainWindow.count += 1
        self.output_window = OutputWindow()
        self.mdi.addSubWindow(self.output_window)

        MainWindow.count += 1
        self.script_window = ScriptWindow()
        self.mdi.addSubWindow(self.script_window)

        MainWindow.count += 1
        self.viewer_window = ViewerWindow()
        self.mdi.addSubWindow(self.viewer_window)

        # QProcess object for external app
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(lambda: self.dataReady("std"))
        self.process.readyReadStandardError.connect(lambda: self.dataReady("error"))
        self.process.finished.connect(lambda: self.update_svg())

        #Connect Slots
        self.script_window.button_exec.clicked.connect(lambda: self.run_script())
        self.script_window.button_read.clicked.connect(lambda: self.read_svg())
        #self.viewer_window.button_save.clicked.connect(lambda: self.save_svg())

        #Assign Shortcuts
        self.shortcut_update = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcut_update.activated.connect(lambda: self.run_script())
        self.shortcut_update = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut_update.activated.connect(lambda: self.read_svg())
        self.shortcut_update = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_update.activated.connect(lambda: self.save_svg())

    def windowaction(self, q):
       if q.text() == "cascade":
          self.mdi.cascadeSubWindows()

       if q.text() == "Tiled":
          self.mdi.tileSubWindows()

    @pyqtSlot()
    def read_svg(self):
        print("READ")
        self.script_window.fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if self.script_window.fname[0]:
            # import script metadata
            svg_tree = ET.parse(self.script_window.fname[0])
            root = svg_tree.getroot()
            for metadata in root.findall("{http://www.w3.org/2000/svg}metadata"):
                for metadatum in metadata:
                    if metadatum.tag == "{https://korintje.com}script":
                        self.script_window.edit.setPlainText(metadatum.text)
                break
            self.run_script()

            # Parse original .svg
            print(self.script_window.fname[0])
            original_svg_tree = ET.parse(self.script_window.fname[0])
            original_root = original_svg_tree.getroot()
            for og in original_root.findall("{http://www.w3.org/2000/svg}g"):
                if "{http://www.inkscape.org/namespaces/inkscape}groupmode" in og.attrib and og.attrib["{http://www.inkscape.org/namespaces/inkscape}groupmode"] == "layer":
                    if "{http://www.inkscape.org/namespaces/inkscape}label" in og.attrib and og.attrib["{http://www.inkscape.org/namespaces/inkscape}label"] == "Layer_mpl":
                        original_root.remove(og)
            register_all_namespaces(self.script_window.fname[0])
            original_svg_tree.write("bkg_temp.svg", encoding="UTF-8", xml_declaration=True)
            self.update_bkg("bkg_temp.svg")

    @pyqtSlot()
    def run_script(self):
        self.output_window.stdout.clear()
        script = self.script_window.edit.toPlainText()
        self.process.start('python3',['-c', script])
        #self.viewer_window.button_save.clicked.connect(lambda: self.save_svg())

    @pyqtSlot()
    def update_svg(self):
        self.viewer_window.view.svg_view.load("temp.svg")

    @pyqtSlot()
    def dataReady(self,err_or_std):
        cursor = self.output_window.stdout.textCursor()
        cursor.movePosition(cursor.End)
        if err_or_std == "std":
            message = self.process.readAllStandardOutput().data().decode("utf8")
            self.output_window.stdout.setTextColor(QColor(48, 255, 48))
        else: #if err_or_std == "error":
            message = self.process.readAllStandardError().data().decode("utf8")
            self.output_window.stdout.setTextColor(QColor(255, 48, 48))
        self.output_window.stdout.insertPlainText(message)
        cursor.insertBlock()
        #self.output_window.setTopLevelWindow()

    @pyqtSlot()
    def update_bkg(self, filename):
        self.viewer_window.bkg.load(filename)

    @pyqtSlot()
    def save_svg(self):
        self.run_script()
        # Parse original .svg
        if self.script_window.fname[0]:
            print(self.script_window.fname[0])
            original_svg_tree = ET.parse(self.script_window.fname[0])
            original_root = original_svg_tree.getroot()
            for og in original_root.findall("{http://www.w3.org/2000/svg}g"):
                if "{http://www.inkscape.org/namespaces/inkscape}groupmode" in og.attrib and og.attrib["{http://www.inkscape.org/namespaces/inkscape}groupmode"] == "layer":
                    if "{http://www.inkscape.org/namespaces/inkscape}label" in og.attrib and og.attrib["{http://www.inkscape.org/namespaces/inkscape}label"] == "Layer_mpl":
                        original_root.remove(og)

        # Insert modified .svg into the original .svg
        modified_svg_tree = ET.parse("temp.svg")
        modified_root = modified_svg_tree.getroot()
        for mg in modified_root.findall("{http://www.w3.org/2000/svg}g"):
            if "id" in mg.attrib and mg.attrib["id"] == "figure_1":
                mg.set("inkscape:groupmode", "layer")
                mg.set("inkscape:label", "Layer_mpl")
                original_root.append(mg)
                print("done")

        # Update the script in the metadata
        for metadata in original_root.findall("{http://www.w3.org/2000/svg}metadata"):
            for metadatum in metadata:
                print(metadatum.tag)
                if metadatum.tag == "{https://korintje.com}script":
                    metadatum.text = self.script_window.edit.toPlainText()
                    print(metadatum.text)
                break

        register_all_namespaces(self.script_window.fname[0])
        original_svg_tree.write("mod_test2.svg", encoding="UTF-8", xml_declaration=True)

def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
