from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
import base64
import requests
from PIL import Image
from io import BytesIO


class MermaidPlotter(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.figure = Figure()
        self.ax_mermaid = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

    def plot(self, graph, mermaid_type=''):
        self.ax_mermaid.clear()
        self._draw_graph(graph)
        self.ax_mermaid.set_title(mermaid_type)
        # Remove the axes lines
        self.ax_mermaid.spines['top'].set_visible(False)
        self.ax_mermaid.spines['right'].set_visible(False)
        self.ax_mermaid.spines['bottom'].set_visible(False)
        self.ax_mermaid.spines['left'].set_visible(False)

        # Remove the ticks
        self.ax_mermaid.yaxis.set_ticks([])
        self.ax_mermaid.xaxis.set_ticks([])
        self.canvas.draw()

    def _draw_graph(self, graph):
        try:
            print(graph)
            graphbytes = graph.encode("ascii")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")
            url = "https://mermaid.ink/img/" + base64_string
            response = requests.get(url)
            print(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                self.ax_mermaid.imshow(img)
            else:
                print(f"Error: Server returned status code {response.status_code}")
        except ValueError as e:
            print(f"An error happened while drawing the graph {e}")

