from OntoGenix_v_1_0.LLM.LlmBase import AbstractLlm


class LlmOntology(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)
        self.auto_completion = self.load_string_from_file(metadata['autocompletion'])
        self.last_prompt = None

    def interact(self, message: str, auto_complete: bool = False):
        try:
            if auto_complete:
                prompt = self.auto_completion.format(prev_input=self.last_prompt, input=message)
            else:
                self.last_prompt = self.instructions.format(input=message)
                prompt = self.last_prompt + self.examples

            response = self.get_api_response(prompt)
            return response

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None