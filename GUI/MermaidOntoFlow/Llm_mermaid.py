from GUI.LLM_base.LlmBase import AbstractLlm
from GUI.tools.text_tools import extract_text


class LlmMermaid(AbstractLlm):

    name = 'MermaidOntoFlow'

    def __init__(self, metadata: dict):
        super().__init__(metadata)

        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.examples = self.load_string_from_file(metadata['examples'])
        self.mermaid = None

    def interact(self, ontology: str):
        try:
            self.current_prompt = self.instructions.format(ontology=ontology, examples=self.examples)
            self.answer = self.get_api_response(self.current_prompt)
            self.mermaid = extract_text(self.answer, start_marker="```mermaid", end_marker="```")
        except ValueError as e:
            print(f"An error occurred while extracting text for the diagram: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_diagram(self):
        return self.mermaid
