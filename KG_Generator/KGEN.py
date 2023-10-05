import traceback
import sys
from io import StringIO
import morph_kgc


class KGen:

    def __init__(self, dataset, destination):
        self.dataset = dataset
        self.destination = destination
        self.output = "DONE"

    def run(self):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            # run the commands needed to generate the knowledge graph
            self._generateKG()
            # updates
            sys.stdout = old_stdout
            
        except Exception:
            # catch exception 
            sys.stdout = old_stdout
            self.output = traceback.format_exc()

        return self.output

    def _generateKG(self):
        graph = morph_kgc.materialize(self.dataset)
        graph.serialize(self.destination, format='ntriples', endoding="utf-8")

 