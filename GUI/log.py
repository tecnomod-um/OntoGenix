from PyQt5 import QtGui, QtCore

class log():
    def __init__(self, logger):
        self.logger = logger

        # Define text formats for different log levels
        self.tf_info = QtGui.QTextCharFormat()
        self.tf_warning = QtGui.QTextCharFormat()
        self.tf_error = QtGui.QTextCharFormat()
        self.tf_answer = QtGui.QTextCharFormat()
        self.tf_manager = QtGui.QTextCharFormat()

        self.tf_info.setForeground(QtGui.QBrush(QtCore.Qt.green))
        self.tf_warning.setForeground(QtGui.QBrush(QtCore.Qt.yellow))
        self.tf_error.setForeground(QtGui.QBrush(QtCore.Qt.red))
        self.tf_answer.setForeground(QtGui.QBrush(QtCore.Qt.white))
        self.tf_manager.setForeground(QtGui.QBrush(QtGui.QColor(255, 165, 0)))  # Set to orange color

        self.text_format = {
            "warning": self.tf_warning,
            "error": self.tf_error,
            "info": self.tf_info,
            "manager": self.tf_manager,
            "answer": self.tf_answer
        }

    def append_log(self, message, level="info", end="\n"):
        # Append the log message with the appropriate format
        self.logger.moveCursor(QtGui.QTextCursor.End)
        self.logger.setCurrentCharFormat(self.text_format[level])
        self.logger.insertPlainText(message + end)

        # Scroll to the bottom to ensure the latest message is visible
        self.logger.verticalScrollBar().setValue(self.logger.verticalScrollBar().maximum())


