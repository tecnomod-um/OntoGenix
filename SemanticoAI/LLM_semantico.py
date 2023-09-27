from LLM_base.LlmBase import AbstractLlm


class LlmSemantico(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        # initialize prompts
        self.instructions = self.load_string_from_file(metadata['instructions'])
        # path setting to write outputs
        self.dataset_path = metadata['dataset']

    def interact(self, ontology: str):
        try:
            prompt = self.instructions.format(
                ontology=ontology
            )

            self.get_api_response(prompt)

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")



