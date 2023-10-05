from typing import Dict, Any, Union
from LLM_base.LlmBase import AbstractLlm


class LlmSemantico(AbstractLlm):
    """
    LlmSemantico is a class that inherits from AbstractLlm and is used for interacting with SemanticoAI.
    It initializes with metadata and has methods to interact with the ontology and handle errors gracefully.
    """

    def __init__(self, metadata: Dict[str, Union[str, Any]]):
        """
        Initializes the LlmSemantico instance.

        Args:
        metadata (Dict[str, Union[str, Any]]): A dictionary containing metadata information.
        It should have 'instructions' key with the path to the instructions file and 'dataset' key with the path to the dataset.
        """
        super().__init__(metadata)  # Call the __init__ method of the parent class AbstractLlm with metadata

        # Load the instructions string from the file specified in metadata
        self.instructions: str = self.load_string_from_file(metadata['instructions'])
        # Set the dataset path from metadata
        self.ontology_path: str = metadata['ontology_path']
        self.chunks_path: str = metadata['chunks_path']
        # initialize memories
        self.codeblock = None

    def interact(self, ontology: str) -> None:
        """
        Interacts with SemanticoAI by sending a prompt and receiving a response.

        Args:
        ontology (str): The ontology string to be formatted into the prompt.

        Raises:
        ValueError: If an error occurs while extracting text.
        """
        try:
            # Format the instructions string with the provided ontology to create the prompt
            prompt: str = self.instructions.format(ontology=ontology)

            # Send the prompt to SemanticoAI and get the response
            self.get_api_response(prompt)
            # extract the codeblock
            self.codeblock = self.extract_text(self.answer, start_marker="```python", end_marker="```")
        except ValueError as e:
            # Print the error message if a ValueError occurs
            print(f"An error occurred while extracting text: {e}")



