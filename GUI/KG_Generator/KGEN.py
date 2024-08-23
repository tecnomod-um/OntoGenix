import traceback
import sys
from io import StringIO
import morph_kgc
from rdflib import Graph

class KGen:
    """
    Class for generating a knowledge graph.

    Args:
        dataset (str): Path to the dataset configuration file.
        destination (str): Path where the generated knowledge graph will be saved.

    Attributes:
        dataset (str): Path to the dataset configuration file.
        destination (str): Path where the generated knowledge graph will be saved.
        error_feedback (str): Error feedback message in case of an exception.
    """

    def __init__(self, dataset: str, destination: str):
        self.dataset = dataset
        self.destination = destination
        self.error_feedback = None

    def run(self):
        """
        Run the knowledge graph generation process.

        Raises:
            Exception: If an error occurs during the generation process.
        """
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            # Run the commands needed to generate the knowledge graph
            self._generateKG()
            # Update attributes
            sys.stdout = old_stdout
            self.error_feedback = "DONE"
        except Exception:
            # Catch exceptions and record error feedback
            sys.stdout = old_stdout
            self.error_feedback = traceback.format_exc()

    def _generateKG(self):
        """
        Generate the knowledge graph using the Morph-KGC library and save it to the specified destination.
        """
        graph = morph_kgc.materialize(self.dataset)
        graph.serialize(self.destination, format='ntriples', encoding="utf-8")
