from PyQt5 import QtGui, QtCore

class Log:
    def __init__(self, logger):
        """
        Initialize the Log class with a QTextEdit logger.
        Define text formats for different log.
        """
        self.logger = logger

        # Define text formats for different log levels
        self.tf_info = QtGui.QTextCharFormat()
        self.tf_warning = QtGui.QTextCharFormat()
        self.tf_error = QtGui.QTextCharFormat()
        self.tf_answer = QtGui.QTextCharFormat()
        self.tf_manager = QtGui.QTextCharFormat()

        # Set the text color for each log level
        self.tf_info.setForeground(QtGui.QBrush(QtCore.Qt.green))
        self.tf_warning.setForeground(QtGui.QBrush(QtCore.Qt.yellow))
        self.tf_error.setForeground(QtGui.QBrush(QtCore.Qt.red))
        self.tf_answer.setForeground(QtGui.QBrush(QtCore.Qt.white))
        self.tf_manager.setForeground(QtGui.QBrush(QtGui.QColor(255, 165, 0)))  # Set to orange color

        # Create a dictionary to map log levels to their corresponding text formats
        self.text_format = {
            "warning": self.tf_warning,
            "error": self.tf_error,
            "info": self.tf_info,
            "manager": self.tf_manager,
            "answer": self.tf_answer
        }

    def append_log(self, message, level="info", end="\n"):
        """
        Append a log message with the specified level to the logger.
        The message will be formatted with the corresponding text format.
        The logger will then scroll to the bottom to ensure the latest message is visible.
        """
        # Move the cursor to the end of the logger
        self.logger.moveCursor(QtGui.QTextCursor.End)

        # Set the current char format to the format corresponding to the log level
        self.logger.setCurrentCharFormat(self.text_format[level])

        # Insert the message into the logger
        self.logger.insertPlainText(message + end)

        # Scroll to the bottom of the logger
        self.logger.verticalScrollBar().setValue(self.logger.verticalScrollBar().maximum())