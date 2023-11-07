from GUI.OntoMapper.LLM_ontomapper import LlmOntoMapper
from GUI.KG_Generator.KGEN import KGen


class RAG_OntoMapper:

    def __init__(self, ontology_mapper, planner_builder):
        self.planner_builder = planner_builder
        self.ontology_mapper = ontology_mapper
        self.max_iter = 2
        self.kgen = None
        self.full_path = None


    def build_kgen(self, base_path, dataset_folder, dataset_file):
        try:
            self.full_path = base_path + '/' + dataset_folder + '/' + dataset_file.split(".")[0]

            self.kgen = KGen(
                dataset=base_path + '/' + dataset_folder + '/config.ini',
                destination=base_path + '/' + dataset_folder + '/data.nt'
            )
        except:
            print("Error building the kgen")

    def generateKG(self):
        try:
            print("################# dataset_path ##############################")
            print(self.full_path + '_rml_mapping_LLM.csv.ttl')

            self.ontology_mapper.save_response(
                self.ontology_mapper.get_rml_codeblock(),
                self.full_path + '_rml_mapping_LLM.csv.ttl',
                mode='w'
            )
            print("save is ok!")

            self.kgen.run()
        except Exception as e:  # Catching the exception and assigning it to variable 'e'.
            print("error while writing the file:", e)
        finally:
            print("------------------------- OUTPUT -------------------------")
            print(self.kgen.error_feedback)