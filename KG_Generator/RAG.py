from OntoMapper.LLM_ontomapper import LlmOntoMapper
from KG_Generator.KGEN import KGen


class RAG_OntoMapper:

    def __init__(self, data_description, ontology_mapper, base_path, dataset_folder):
        self.data_description = data_description
        self.ontology_mapper = ontology_mapper
        self.kgen = KGen(
            dataset=base_path + dataset_folder + '/config.ini',
            destination=base_path + dataset_folder + '/data.nt'
        )
        self.max_iter = 2
        self.cont = 0
        self.error_feedback = "NO ERROR"

    async def loop(self):


        while True:
            print(output)
            if self.error_feedback == "DONE":
                print("everything is ok")
                break
            elif self.cont >= self.max_iter:
                print("######################################################")
                print("Reached maximum iterations")
                print(output)
            elif self.error_feedback != "DONE" and self.cont < self.max_iter:
                await self.iterate()

    async def iterate(self):
        # generate the rml code for mapping the ontology with regards the source data.
        async for chunk_data in self.ontology_mapper.interact(rationale=self.data_description, error=self.error_feedback):
            print(chunk_data, end='')

        try:
            self.ontology_mapper.save_response(
                self.ontology_mapper.get_rml_codeblock(),
                self.ontology_mapper.dataset_path + '_rml_mapping_LLM.csv.ttl',
                mode='w'
            )
            print("save is ok!")
        except:
            print("error while writing the file.")

        self.error_feedback = self.kgen.run()
        print("------------------------- OUTPUT -------------------------")
        print(self.error_feedback)

