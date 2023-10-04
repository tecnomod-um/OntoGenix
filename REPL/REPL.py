import traceback
import sys
from io import StringIO

class PythonREPL:
    def __init__(self):
        pass        

    def run(self, command):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(command)
            sys.stdout = old_stdout
            output = mystdout.getvalue()
        except Exception:
            sys.stdout = old_stdout
            output = traceback.format_exc()

        return output
