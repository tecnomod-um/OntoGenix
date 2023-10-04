from PyQt5 import QtGui, QtCore

from PyQt5 import QtGui, QtCore


class log():
    def __init__(self, logger):
        self.logger = logger
        self.logger.setCenterOnScroll(True)

        self.tf = QtGui.QTextCharFormat()
        self.tf_yellow = QtGui.QTextCharFormat()
        self.tf_green = QtGui.QTextCharFormat()
        self.tf_red = QtGui.QTextCharFormat()

        self.tf_yellow.setForeground(QtGui.QBrush(QtCore.Qt.yellow))
        self.tf_green.setForeground(QtGui.QBrush(QtCore.Qt.green))
        self.tf_red.setForeground(QtGui.QBrush(QtCore.Qt.red))

    def _print(self, text, text_format):
        self.logger.setCurrentCharFormat(text_format)
        self.logger.appendPlainText(text)
        self.logger.centerCursor()
        self.logger.repaint()

    def myprint(self, text):
        self._print(text, self.tf)

    def myprint_in(self, text):
        self._print("< " + text, self.tf_yellow)

    def myprint_out(self, text):
        self._print("> " + text, self.tf_green)

    def myprint_error(self, text):
        self._print(text, self.tf_red)

    def clear(self):
        self.logger.clear()