# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)
@email: %(mikel1982mail@gmail.com)
@institution: %( Departamento de informática y sistemas, Universidad de Murcia )
@DOI:
"""
from GUI.GuiBehavior import GuiBehavior

from PyQt5.QtWidgets import QApplication
import sys


class APP(QApplication):
    def __init__(self):
        QApplication.__init__(self, [''])
        self.load_style()
        # --- Launch GUI ---
        self.gui = GuiBehavior()
        # --- exec ---
        sys.exit(self.exec_())

    def load_style(self):
        with open("GUI/css/Genetive.qss") as f:
            self.setStyleSheet(f.read())


if __name__ == '__main__':
    main = APP()
