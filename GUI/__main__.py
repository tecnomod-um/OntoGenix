# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)
@email: %(mikel1982mail@gmail.com)
@institution: %( Departamento de informática y sistemas, Universidad de Murcia )
@DOI:
"""
from GUI.GuiManager.GuiBehavior import GuiBehavior
import os, argparse

from PyQt5.QtWidgets import QApplication # pylint: disable = no-name-in-module
import sys

def dir_path(path):
    """
        Auxiliar function for parsing path type in argparse.ArgumentParser(type=?) variable
    """
    if path != None and (os.path.exists(os.path.join(os.getcwd(), path))
                    or os.path.exists(os.path.join(path))):
        return path
    else:
        return None

#api_model : str = 'gpt-3.5-turbo'
#api_model : str = 'gpt-4-1106-preview'
#api_model : str = 'gpt-4o-2024-05-13' # gpt-4o
class APP(QApplication):
    def __init__(self):
        parser = argparse.ArgumentParser(usage="python -m GUI [--client OR -c <(openai|azure)>] \n\
                                         [--ssl-cert OR -sc <path_to_cert>] [--api-model OR -am <api_model>] \n\
                                         [--extension-mapping OR -em <mapping_extension>]")
        # NOTE: --client (PUBLIC|AZURE) --ssl-cert <path_to_cert> --api-model <api_model> --extension-mapping <mapping_extension>
        parser.add_argument("--api-model", "-am", dest="api_model", default="gpt-4o-2024-05-13") # ""
        parser.add_argument("--client", "-c", dest="client", default="openai")
        parser.add_argument("--extension-mapping", "-em", dest="mapping_extension", default="ttl")
        parser.add_argument("--ssl-cert", "-sc", dest="ssl_cert", default=None, type=dir_path)
        argv = parser.parse_known_args()[0]
        QApplication.__init__(self, [''])
        self.load_style()
        # --- Launch GUI ---
        self.gui = GuiBehavior(argv)
        # --- exec ---
        sys.exit(self.exec_())

    def load_style(self, path="./GUI/css/Manjaro.qss"):
        """
            Read the style of the GUI from the QSS file
        """
        if not hasattr(self, "app_style"):
            with open(path, encoding="utf-8") as f:
                self.app_style = f.read()
        self.setStyleSheet(self.app_style)

if __name__ == '__main__':
    main = APP()
