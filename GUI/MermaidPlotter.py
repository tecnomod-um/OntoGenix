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
    """
    A widget that plots graphs using the Mermaid syntax.

    This class inherits from QWidget and integrates matplotlib for plotting,
    and PIL for image processing. It fetches the graph image from the mermaid.ink
    service and displays it in the widget.

    Attributes:
        figure (Figure): Matplotlib Figure object for the plot.
        ax_mermaid (Axes): The Axes object of matplotlib for plotting.
        canvas (FigureCanvas): The canvas on which the figure is drawn.
        toolbar (NavigationToolbar): Navigation toolbar for the plot canvas.
        layout (QVBoxLayout): Layout manager for the widget.
    """

    def __init__(self, parent: QWidget = None):
        """
        Initializes the MermaidPlotter widget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        self.figure = Figure()
        self.ax_mermaid = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

    def plot(self, graph: str, mermaid_type: str = ''):
        """
        Plots the given Mermaid graph.

        Clears the current plot, draws the new graph, and updates the canvas.

        Args:
            graph (str): The graph in Mermaid syntax to be plotted.
            mermaid_type (str, optional): Title for the graph. Defaults to an empty string.
        """
        self.ax_mermaid.clear()
        self._draw_graph(graph)
        self.ax_mermaid.set_title(mermaid_type)

        # Configuring the axes appearance
        for spine in self.ax_mermaid.spines.values():
            spine.set_visible(False)
        self.ax_mermaid.yaxis.set_ticks([])
        self.ax_mermaid.xaxis.set_ticks([])

        self.canvas.draw()

    def _draw_graph(self, graph: str):
        """
        Helper method to draw the graph.

        This method encodes the graph string, sends a request to the Mermaid service,
        and processes the response to display the graph as an image.

        Args:
            graph (str): The graph in Mermaid syntax to be drawn.
        """
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
