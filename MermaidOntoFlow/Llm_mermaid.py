from LLM_base.LlmBase import AbstractLlm


class LlmMermaid(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)

        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.examples = self.load_string_from_file(metadata['examples'])

    def interact(self, ontology: str):
        try:
            self.current_prompt = self.instructions.format(ontology=ontology, examples=self.examples)
            self.get_api_response(self.current_prompt)

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_diagram(self):
        return self.extract_text(self.answer, start_marker="```mermaid", end_marker="```")
