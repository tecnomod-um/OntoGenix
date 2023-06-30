from LLM_base.LlmBase import AbstractLlm


class LlmSemantic(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions = self.load_string_from_file(metadata['instructions'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']
        # initialize memories
        self.semantic_descriptions = dict()

    def interact(self, ontology: str, auto_complete: bool = False):
        try:
            prompt = self.instructions.format(
                ontology=ontology
            )

            response = self.get_api_response(prompt)
            print('##################################\n', response)
            dictionary_str = self.extract_text(response, "START", "FINISH")

            self.save_response(dictionary_str, self.dataset_path + '_ontology_semantic_description_LLM.ttl', mode='w')
            print(type(dictionary_str))

            self.semantic_descriptions = eval(dictionary_str)

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")

