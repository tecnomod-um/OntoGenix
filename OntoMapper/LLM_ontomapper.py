from LLM_base.LlmBase import AbstractLlm


class LlmOntoMapper(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions = self.load_string_from_file(metadata['instructions'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']
        # initialize memories
        self.rml_code_str = None

    def interact(self, json_data: str, ontology: str, auto_complete: bool = False):
        try:
            prompt = self.instructions.format(
                json_data=json_data,
                ontology=ontology
            )

            response = self.get_api_response(prompt)
            self.rml_code_str = self.extract_text(response, "START", "FINISH")

            file = self.dataset_path + '_rml_mapping_LLM.ttl'
            with open(file, 'w') as f:
                f.write(self.rml_code_str)

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")

