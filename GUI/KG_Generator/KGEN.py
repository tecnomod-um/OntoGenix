
"""
    This module contains functionality for the process of Knowledge Graph Generation (KG(G)en)
"""
import traceback
import sys
from io import StringIO
import morph_kgc

class KGen:
    """
        Generates the triplets (*.nt format) from the given config_ini_file and stores it in the
        specified destination directory.
    """

    def __init__(self, config_ini_file : str, dest_nt_file : str):
        """
            Initialize the data for the class.
        """
        self.config_ini_file : str = config_ini_file
        self.dest_nt_file : str = dest_nt_file
        self.error_feedback : str = None
        self.is_done : bool = False

    def reset_internal_state(self):
        """
            Resets internal state
        """
        self.error_feedback = None
        self.is_done = False

    def run(self):
        """
            Attempts to generate the knowledge graph for the given config_ini_file.
            For that matter, it changes the default system stdout pipeline to write
            the output of the method in the destination directory file (in .nt format).
        """
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            # run the commands needed to generate the knowledge graph
            self._generateKG()
            # updates
            sys.stdout = old_stdout
            self.error_feedback = "DONE"
            self.is_done = True
        #except FileNotFoundError as ex:
        #    print(ex)
        except Exception as e:
            # catch exception
            #print(e)
            self.error_feedback = traceback.format_exc()
            self.is_done = False
            raise e # raise e from None # If we want to re-raise "Exception" instead of the Exception's subclass
        finally:
            sys.stdout = old_stdout

    def _generateKG(self):
        """
            Generates the knowledge graph with the morph_kgc.materialize() method.
            It does it in 'ntriples' (.nt) format with default "utf-8" encoding.

            NOTE: It gives the following information message in windows platform:
                INFO (WINDOWS): Parallelization is not supported for win32 when running as a library.
                If you need to speed up your data integration pipeline, please run through the command line.

            TODO: When the column does not exist it throws an error like this example:
                ValueError: Usecols do not match columns, columns expected but not found: ['ReviewId']
        """
        graph = morph_kgc.materialize(self.config_ini_file)
        graph.serialize(self.dest_nt_file, format='ntriples', encoding="utf-8")
