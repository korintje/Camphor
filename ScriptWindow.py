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
