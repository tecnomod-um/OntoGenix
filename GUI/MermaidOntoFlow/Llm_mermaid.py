from GUI.LLM_base.LlmBase import AbstractLlm

class LlmMermaid(AbstractLlm):
    """
    A class to manage interactions with a language learning model for generating Mermaid diagrams.

    This class extends AbstractLlm and specializes in formatting prompts for Mermaid diagram generation and
    extracting the resulting diagram code from the LLM's responses.

    Attributes:
        instructions (str): Template for instructions to the LLM for generating Mermaid diagrams.
        examples (str): Example data to assist in diagram generation.
    """

    def __init__(self, metadata: dict):
        """
        Initialize the LlmMermaid object.

        Args:
            metadata (dict): Metadata for the LLM, including file paths for instructions and examples.
        """
        super().__init__(metadata)
        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.examples = self.load_string_from_file(metadata['examples'])

    def interact(self, ontology: str):
        """
        Perform an interaction with the LLM to generate a Mermaid diagram.

        The method formats a prompt using ontology data and sends it to the LLM. The response is expected
        to include a Mermaid diagram.

        Args:
            ontology (str): The ontology data used for generating the Mermaid diagram.
        """
        try:
            self.current_prompt = self.instructions.format(ontology=ontology, examples=self.examples)
            self.get_api_response(self.current_prompt)

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_diagram(self) -> str:
        """
        Extract the Mermaid diagram code from the LLM's response.

        Returns:
            str: The extracted Mermaid diagram code.
        """
        return self.extract_text(self.answer, start_marker="```mermaid", end_marker="```")
