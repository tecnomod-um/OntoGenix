from OntoGenix_v_1_1.LLM.LlmBase import AbstractLlm


class LlmOntoMapper(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        self.instructions = self.load_string_from_file(metadata['instructions'])

    def interact(self, json_data: str, ontology: str, auto_complete: bool = False):
        try:

            prompt = self.instructions.format(
                json_data=json_data,
                ontology=ontology
            )

            response = self.get_api_response(prompt)
            rml_code_str = self.extract_text(response, "RML Mapping:\n", "Finish Statement: FINISH")
            return rml_code_str

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None

