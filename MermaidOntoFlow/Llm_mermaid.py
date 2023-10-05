from LLM_base.LlmBase import AbstractLlm


class LlmMermaid(AbstractLlm):

    def __init__(self, metadata: dict):
        super().__init__(metadata)

        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.examples = self.load_string_from_file(metadata['examples'])
        self.codeblock = None

    def interact(self, ontology: str):
        try:
            self.current_prompt = self.instructions.format(ontology=ontology, examples=self.examples)
            self.get_api_response(self.current_prompt)
            self.codeblock = self.extract_text(self.answer, "'''mermaid", "'''")
        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt
