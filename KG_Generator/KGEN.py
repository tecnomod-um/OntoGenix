import traceback
import sys
from io import StringIO
import morph_kgc


class KGen:

    def __init__(self, dataset, destination):
        self.dataset = dataset
        self.destination = destination
        self.error_feedback = "NO ERROR"

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

#
# with open('./datasets/eCommerce/data.csv', 'r', encoding='latin-1') as f:
#     for line_no, line in enumerate(f, 1):
#         try:
#             line.encode('us-ascii')
#         except UnicodeEncodeError:
#             print(f"Non-ASCII character on line {line_no}: {line.strip()}")
#
#
# with open('./datasets/eCommerce/data.csv', 'r', encoding='latin-1') as source_file:
#     contents = source_file.read()
#     print('terminado')
#
# with open('./datasets/eCommerce/data_utf8.csv', 'w', encoding='utf-8') as target_file:
#     target_file.write(contents)
#     print('terminado')



 