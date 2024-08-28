from GUI.OntoMapper.LLM_ontomapper import LlmOntoMapper
from GUI.PlanSage.LLM_planner import LlmPlanner
from GUI.KG_Generator.KGEN import KGen
from GUI.GuiManager.metadata import DatasetMetadata

class RAG_OntoMapper:
    """
        Undocumented.
        TODO: Review current file name.
    """

    def __init__(self, ontology_mapper : LlmOntoMapper, planner_builder: LlmPlanner, max_iter : int = 2):
        self.planner_builder : LlmPlanner = planner_builder
        self.ontology_mapper : LlmOntoMapper = ontology_mapper
        self.max_iter : int = max_iter
        self.kgen : KGen = None
        self.dataset_metadata : DatasetMetadata = None

    def build_kgen(self, dataset : DatasetMetadata = None):
        """
            Builds the KGEN object from the dataset's metadata.
        """
        try:
            self.dataset_metadata = dataset or self.dataset_metadata
            self.kgen = KGen(
                config_ini_file=self.dataset_metadata.dataset_config_path,  # Configuration file
                dest_nt_file=self.dataset_metadata.dataset_triplets_path    # Triplets file
            )
        except Exception as ex:
            print("Error building the kgen:", ex)

    def generateKG(self):
        """
            Generates the KGEN object from the RML and generates the mapping
        """
        try:
            print("################# dataset_path ##############################")
            print(self.dataset_metadata.dataset_mapping_path)

            self.ontology_mapper.save_response(
                self.ontology_mapper.get_rml_codeblock(),
                self.dataset_metadata.dataset_mapping_path,
                mode='w'
            )
            print("save is ok!")
            # TODO: generate only the RML. It should be necessary to click on an additional button to generate the mapping (the most costly operation)
            self.kgen.run()
        except Exception as e:  # Catching the exception and assigning it to variable 'e'.
            print("error while writing the file:", e)
            raise e
        finally:
            print("------------------------- OUTPUT -------------------------")
            print(self.kgen.error_feedback)