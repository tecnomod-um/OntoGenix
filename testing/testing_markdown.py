import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPlainTextEdit, QHBoxLayout, QWidget
from markdown import markdown


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a widget for central layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set main layout
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # Raw Markdown Editor
        self.md_edit = QTextEdit(self)
        self.md_edit.textChanged.connect(self.update_preview)
        layout.addWidget(self.md_edit)

        # Rendered HTML Preview
        self.html_preview = QTextEdit(self)
        self.html_preview.setReadOnly(True)
        layout.addWidget(self.html_preview)

        # Sample: You can set some initial text if you want
        self.md_edit.setPlainText("# Hello Markdown\nThis is *italic* and **bold** text!")

    def update_preview(self):
        md_text = self.md_edit.toPlainText()
        html = markdown(md_text)
        self.html_preview.setHtml(html)


app = QApplication(sys.argv)
window = MainWindow()
window.resize(600, 400)  # Adjust the size to your preference
window.show()
sys.exit(app.exec_())
