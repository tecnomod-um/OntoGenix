from OntoMapper.LLM_ontomapper import LlmOntoMapper
from KG_Generator.KGEN import KGen


class RAG_OntoMapper:

    def __init__(self, ontology_mapper, planner_builder):
        self.planner_builder = planner_builder
        self.ontology_mapper = ontology_mapper
        self.max_iter = 2
        self.cont = 0
        self.kgen = None

    def build_kgen(self, base_path, dataset_folder):
        try:
            self.kgen = KGen(
                dataset=base_path + dataset_folder + '/config.ini',
                destination=base_path + dataset_folder + '/data.nt'
            )
        except:
            print("Error building the kgen")

    async def loop(self):
        while True:
            if self.kgen.error_feedback == "DONE":
                print("everything is ok")
                break
            elif self.cont >= self.max_iter:
                print("Reached maximum iterations")
            elif self.kgen.error_feedback != "DONE" and self.cont < self.max_iter:
                await self.iterate()

    async def iterate(self):
        print(self.ontology_mapper)
        # generate the rml code for mapping the ontology with regards the source data.
        async for _ in self.ontology_mapper.interact(rationale=self.planner_builder.data_description,
                                                     error=self.kgen.error_feedback):
            pass

        try:
            print(self.ontology_mapper.answer)
            print(self.ontology_mapper.get_rml_codeblock())
            print(self.ontology_mapper.dataset_path + '_rml_mapping_LLM.csv.ttl')
            self.ontology_mapper.save_response(
                self.ontology_mapper.get_rml_codeblock(),
                self.ontology_mapper.dataset_path + '_rml_mapping_LLM.csv.ttl',
                mode='w'
            )
            print("save is ok!")

            self.kgen.run()
        except:
            print("error while writing the file.")
        finally:
            print("------------------------- OUTPUT -------------------------")
            print(self.kgen.error_feedback)
