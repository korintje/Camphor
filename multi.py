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
        #self.process.started.connect(lambda: self.runButton.setEnabled(False))
        #self.process.finished.connect(lambda: self.runButton.setEnabled(True))
        self.process.finished.connect(lambda: self.update_svg())

        #Connect Slots
        self.script_window.button_exec.clicked.connect(lambda: self.run_script())
        self.script_window.button_read.clicked.connect(lambda: self.read_svg())
        self.viewer_window.button_save.clicked.connect(lambda: self.save_svg())


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
        #self.output_window.errout.clear()
        script = self.script_window.edit.toPlainText()
        self.process.start('python3',['-c', script])
        self.viewer_window.button_save.clicked.connect(lambda: self.save_svg())
        #connect(cameraControl, SIGNAL(finished(int , QProcess::ExitStatus )), this, SLOT(on_cameraControlExit(int , QProcess::ExitStatus )));

    @pyqtSlot()
    def update_svg(self):
        self.viewer_window.view.load("temp.svg")

    @pyqtSlot()
    def dataReady(self,err_or_std):
        cursor = self.output_window.stdout.textCursor()
        cursor.movePosition(cursor.End)
        if err_or_std == "std":
            message = self.process.readAllStandardOutput().data().decode("utf8")
            self.output_window.stdout.setTextColor(QColor(48, 255, 48))
            #self.output_window.tabs.setCurrentIndex(0)
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


class ScriptWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.title = "Code Editor"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 960

        self.initUI()

    def initUI(self):
        # Set the title and window size
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create parts
        self.edit = CodeEditor(self)
        self.edit.setPlainText("Open an existing .svg file or write a script")

        self.button_exec = QPushButton("Run", self)
        self.button_exec.setToolTip("Update the graph")

        self.button_read = QPushButton("Open", self)
        self.button_read.setToolTip("Read .svg file")
        #self.button_read.clicked.connect(lambda: self.read_svg())

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(self.edit, 0,0,1,2)
        self.grid.addWidget(self.button_exec, 1,0,1,1)
        self.grid.addWidget(self.button_read, 1,1,1,1)
        self.setLayout(self.grid)

        self.show()

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

        # Initialize tab screen
        #self.tabs = QTabWidget()
        #self.tab1 = QWidget()
        #self.tab2 = QWidget()
        #self.tabs.resize(300,200)

        # Create parts
        self.stdout = QTextEdit(self)
        self.stdout.setReadOnly(True)
        self.stdout.setUndoRedoEnabled( False )
        self.stdout.setStyleSheet("background-color: rgb(36, 36, 36);" "color: rgb(48, 255, 48)")
        self.stdout.cursor = self.stdout.textCursor()

        #self.errout = QTextEdit(self)
        #self.errout.setReadOnly(True)
        #self.errout.setStyleSheet("background-color: rgb(36, 36, 36);" "color: rgb(255, 48, 48)")
        #self.errout.cursor = self.errout.textCursor()

        # Add tabs
        #self.tabs.addTab(self.stdout,"Stdout")
        #self.tabs.addTab(self.errout,"Errout")

        self.grid = QGridLayout()
        #self.grid.addWidget(self.tabs)
        #self.grid.setSpacing(10)
        self.grid.addWidget(self.stdout, 2,0,1,1)
        #self.grid.addWidget(self.errout, 2,1,1,1)
        self.setLayout(self.grid)

        self.show()

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

class LineNumberArea(QWidget):

    def __init__(self, editor):
        super().__init__(editor)
        self.myeditor = editor


    def sizeHint(self):
        return Qsize(self.editor.lineNumberAreaWidth(), 0)


    def paintEvent(self, event):
        self.myeditor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent = None):
        super(CodeEditor,self).__init__(parent)
        self.highlight = syntax.PythonHighlighter(self.document())

        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)


    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space


    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)


    def updateLineNumberArea(self, rect, dy):

        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(),
                       rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)


    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect();
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                    self.lineNumberAreaWidth(), cr.height()))


    def lineNumberAreaPaintEvent(self, event):
        mypainter = QPainter(self.lineNumberArea)

        mypainter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                mypainter.setPen(Qt.black)
                mypainter.drawText(0, top, self.lineNumberArea.width(), height,
                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1


    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            lineColor = QColor(Qt.yellow).lighter(185)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

def main():
    app = QApplication(sys.argv)
    #QTextCodec.setCodecForCStrings( QTextCodec.codecForLocale() )
    ex = MainWindow()
    ex.show()
    #console = PythonConsole()
    #console.show()
    #console.eval_in_thread()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
