from GUI.OntoMapper.LLM_ontomapper import LlmOntoMapper
from GUI.KG_Generator.KGEN import KGen
from typing import Optional

class RAG_OntoMapper:
    """
    Class for mapping ontologies and generating knowledge graphs (KGs).

    Args:
        ontology_mapper (LlmOntoMapper): An instance of LlmOntoMapper for ontology mapping.
        planner_builder: An instance for building a planner (type can be specified).

    Attributes:
        planner_builder: An instance for building a planner.
        ontology_mapper (LlmOntoMapper): An instance of LlmOntoMapper for ontology mapping.
        max_iter (int): Maximum number of iterations.
        kgen: An instance for generating the knowledge graph.
        full_path (str): Full path to the dataset.
    """

    def __init__(self, ontology_mapper: LlmOntoMapper, planner_builder: Optional[type]):
        self.planner_builder = planner_builder
        self.ontology_mapper = ontology_mapper
        self.max_iter = 2
        self.kgen = None
        self.full_path = None

    def build_kgen(self, base_path: str, dataset_folder: str, dataset_file: str):
        """
        Build a knowledge graph generator (KGen) instance.

        Args:
            base_path (str): Base path for the dataset.
            dataset_folder (str): Folder containing the dataset.
            dataset_file (str): Dataset file name.

        Raises:
            Exception: If an error occurs during KGen initialization.
        """
        try:
            self.full_path = f"{base_path}/{dataset_folder}/{dataset_file.split('.')[0]}"
            self.kgen = KGen(
                dataset=f"{base_path}/{dataset_folder}/config.ini",
                destination=f"{base_path}/{dataset_folder}/data.nt"
            )
        except Exception as e:
            print("Error building the kgen:", e)

    def generateKG(self):
        """
        Generate the knowledge graph.

        Raises:
            Exception: If an error occurs during KG generation.
        """
        try:
            print("################# dataset_path ##############################")
            print(f"{self.full_path}_rml_mapping_LLM.csv.ttl")

            self.ontology_mapper.save_response(
                self.ontology_mapper.get_rml_codeblock(),
                f"{self.full_path}_rml_mapping_LLM.csv.ttl",
                mode='w'
            )
            print("save is ok!")

            self.kgen.run()
        except Exception as e:
            print("Error while writing the file:", e)
        finally:
            print("------------------------- OUTPUT -------------------------")
            print(self.kgen.error_feedback)
