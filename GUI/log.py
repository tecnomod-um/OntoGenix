from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QTextEdit  # Assuming you're using PyQt5

class log:
    """
    A utility class for logging messages with different formats based on log levels.

    This class is designed to append messages to a given logger widget with
    specific text formatting based on the log level (info, warning, error, manager, answer).

    Attributes:
        logger (QTextEdit): The text edit widget where logs are displayed.
        text_format (dict): A dictionary mapping log levels to their respective text formats.
    """

    def __init__(self, logger: QTextEdit):
        """
        Initializes the log class with a logger widget.

        Args:
            logger (QTextEdit): The logger widget where the logs will be displayed.
        """
        self.logger = logger

        # Define text formats for different log levels
        self.tf_info = QtGui.QTextCharFormat()
        self.tf_warning = QtGui.QTextCharFormat()
        self.tf_error = QtGui.QTextCharFormat()
        self.tf_answer = QtGui.QTextCharFormat()
        self.tf_manager = QtGui.QTextCharFormat()

        # Set colors for different log levels
        self.tf_info.setForeground(QtGui.QBrush(QtCore.Qt.green))
        self.tf_warning.setForeground(QtGui.QBrush(QtCore.Qt.yellow))
        self.tf_error.setForeground(QtGui.QBrush(QtCore.Qt.red))
        self.tf_answer.setForeground(QtGui.QBrush(QtCore.Qt.white))
        self.tf_manager.setForeground(QtGui.QBrush(QtGui.QColor(255, 165, 0)))  # Orange color

        # Mapping of log levels to their corresponding text formats
        self.text_format = {
            "warning": self.tf_warning,
            "error": self.tf_error,
            "info": self.tf_info,
            "manager": self.tf_manager,
            "answer": self.tf_answer
        }

    def append_log(self, message: str, level: str = "info", end: str = "\n"):
        """
        Appends a log message to the logger with the format based on the specified level.

        Args:
            message (str): The log message to append.
            level (str, optional): The log level, affects the message format. Defaults to "info".
            end (str, optional): The end character to append after the message. Defaults to "\n".
        """
        # Move cursor to the end and set the character format based on the log level
        self.logger.moveCursor(QtGui.QTextCursor.End)
        self.logger.setCurrentCharFormat(self.text_format[level])
        self.logger.insertPlainText(message + end)

        # Scroll to the bottom to ensure the latest message is visible
        self.logger.verticalScrollBar().setValue(self.logger.verticalScrollBar().maximum())
