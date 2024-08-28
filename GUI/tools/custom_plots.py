import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
import base64
import requests
from PIL import Image
from io import BytesIO


def plot_word_embeddings(result, labels, color='b'):
    plt.scatter(result[:, 0], result[:, 1], color=color)
    for i, node in enumerate(labels):
        plt.annotate(node, (result[i, 0], result[i, 1]))


def plot_mermaid(diagram: str, path: str = None) -> None:
    """
    Plot a Mermaid diagram by converting it to an image and displaying it using Matplotlib.

    Args:
        diagram (str): The Mermaid diagram string.

    Returns:
        None
        :param diagram:
        :param path:
    """
    try:
        graphbytes = diagram.encode("ascii")
        base64_bytes = base64.b64encode(graphbytes)
        base64_string = base64_bytes.decode("ascii")
        url = "https://mermaid.ink/img/" + base64_string
        response = requests.get(url)
        print('response status code should be 200: ', response.status_code)
        img = Image.open(BytesIO(response.content))

        # plot
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_aspect('equal')
        ax.imshow(img)
        plt.axis('off')
        ax.axis('off')
        # Maximize the figure
        manager = plt.get_current_fig_manager()
        manager.window.showMaximized()
        # save figure
        if path:
            plt.savefig(path, format='png', dpi=300)
        plt.show()

    except Exception as e:
        # Handle any exception that occurs during the diagram plotting process
        print(f"An error occurred: {str(e)}")
