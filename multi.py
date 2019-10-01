import sys
from threading import Thread
from pyqtconsole.console import PythonConsole
from PyQt5 import QtSvg
from PyQt5.QtCore import pyqtSlot, QProcess
from PyQt5.QtGui import QKeySequence, QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QFileDialog, QAction, QPlainTextEdit, QGridLayout, QDialog, QLabel, QMainWindow, QMdiArea, QMdiSubWindow, QShortcut
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO

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
        self.process = QProcess(self)

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
        self.script_window = ScriptWindow()
        self.mdi.addSubWindow(self.script_window)

        MainWindow.count += 1
        self.viewer_window = ViewerWindow()
        self.mdi.addSubWindow(self.viewer_window)

        #Connect Slots
        self.script_window.button_exec.clicked.connect(lambda: self.update_svg())
        self.script_window.button_read.clicked.connect(lambda: self.read_svg())
        self.viewer_window.button_save.clicked.connect(lambda: self.save_svg())
        self.process.readyReadStandardOutput.connect(lambda: self.printOutput())

        #Assign Shortcuts
        self.shortcut_update = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcut_update.activated.connect(lambda: self.update_svg())
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
            self.update_svg()

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
    def update_svg(self):
        script = self.script_window.edit.toPlainText()
        #exec(script)
        execute_script(script)
        self.viewer_window.view.load("temp.svg")

    @pyqtSlot()
    def execute_script(self, script):
        #self.process.start("python -c {}".format(script))
        self.process.start('python -c "hello world"')
        self.process.waitForFinished()

    @pyqtSlot()
    def printOutput(self):
        byte = self.process.readAllStandardOutput().data()
        self.addLine(str(byte))

    @pyqtSlot()
    def addLine(self):
        self.script_window.stdout.cursor.movePosition(QTextCursor.End)
        self.script_window.stdout.cursor.insertText(str(line))
        self.script_window.stdout.cursor.insertBlock()
        self.linecount += 1
        if self.linecount > self.maxLine:
            self.script_window.stdout.cursor.movePosition(QTextCursor.Start)
            self.script_window.stdout.cursor.select(QTextCursor.BlockUnderCursor)

    @pyqtSlot()
    def update_bkg(self, filename):
        #script = self.script_window.edit.toPlainText()
        #exec(script)
        self.viewer_window.bkg.load(filename)

    @pyqtSlot()
    def save_svg(self):
        self.update_svg()
        # Parse original .svg
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


class ScriptWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.title = "ScriptWindow"
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
        self.edit = QPlainTextEdit(self)
        self.edit.setPlainText("Open an existing .svg file or write a script")

        self.stdout = QPlainTextEdit(self)
        self.stdout.cursor = self.stdout.textCursor()

        self.button_exec = QPushButton("Update", self)
        self.button_exec.setToolTip("Update the graph")

        self.button_read = QPushButton("Open", self)
        self.button_read.setToolTip("Read .svg file")
        #self.button_read.clicked.connect(lambda: self.read_svg())

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(self.edit, 0,0,1,2)
        self.grid.addWidget(self.button_exec, 1,0,1,1)
        self.grid.addWidget(self.button_read, 1,1,1,1)
        self.grid.addWidget(self.stdout, 2,0,1,2)
        self.setLayout(self.grid)

        self.show()


class ViewerWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.title = "ViewerWindow"
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
        #self.ext = QtSvg.QSvgWidget("ichimatsu.svg")
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

def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    #console = PythonConsole()
    #console.show()
    #console.eval_in_thread()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
