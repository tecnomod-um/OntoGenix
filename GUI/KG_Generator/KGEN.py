import traceback
import sys
from io import StringIO
import morph_kgc


class KGen:

    def __init__(self, dataset, destination):
        self.dataset = dataset
        self.destination = destination
        self.error_feedback = None

    def run(self):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            # run the commands needed to generate the knowledge graph
            self._generateKG()
            # updates
            sys.stdout = old_stdout
            self.error_feedback = "DONE"
        except Exception:
            # catch exception
            sys.stdout = old_stdout
            self.error_feedback = traceback.format_exc()

    def _generateKG(self):
        graph = morph_kgc.materialize(self.dataset)
        graph.serialize(self.destination, format='ntriples', encoding="utf-8")


