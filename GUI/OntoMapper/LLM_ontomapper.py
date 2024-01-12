from GUI.LLM_base.LlmBase import AbstractLlm
from typing import Optional


class LlmOntoMapper(AbstractLlm):
    """
    A class representing an ontology mapper using a language learning model.

    This class extends the AbstractLlm class and specializes in ontology mapping tasks. It manages interactions
    with the LLM using predefined prompts for generating RML code based on the provided rationale and error handling.

    Attributes:
        instructions (str): The template for generating instructions to the LLM.
        error_instructions (str): The template for generating error handling instructions.
        rml_codeblock (str): The generated RML code block after interaction with the LLM.
        _dataset_path (str): The path to the dataset used in the LLM interactions.
    """

    def __init__(self, metadata: dict):
        """
        Initialize the LlmOntoMapper object.

        Parameters:
            metadata (dict): Metadata for the LLM, including file paths and configurations.
        """
        super().__init__(metadata)
        self.instructions = self.load_string_from_file(metadata['instructions'])
        self.error_instructions = self.load_string_from_file(metadata['error_instructions'])
        self._dataset_path = metadata['dataset']
        self.rml_codeblock = None

    @property
    def dataset_path(self):
        """
        Getter for the dataset path.

        Returns:
            str: The path to the dataset.
        """
        return self._dataset_path

    @dataset_path.setter
    def dataset_path(self, path: str):
        """
        Setter for the dataset path.

        Parameters:
            path (str): The new path for the dataset.

        Raises:
            ValueError: If the provided path is not a string.
        """
        if not isinstance(path, str):
            raise ValueError("Path must be a string!")
        self._dataset_path = path

    async def interact(self, rationale: Optional[str] = None, error: Optional[str] = None):
        """
        Perform an interaction with the LLM for ontology mapping.

        Parameters:
            rationale (Optional[str]): The rationale for the mapping task.
            error (Optional[str]): Any error information to be handled.

        Yields:
            str: Chunks of the response from the LLM.

        Exceptions:
            ValueError: Catches and prints any ValueError that occurs during the interaction.
        """
        try:
            csv_data = self._dataset_path.split('/')[-1]
            if rationale and not error:
                self.current_prompt = self.instructions.format(rationale=rationale, csv_data=csv_data)
            elif rationale and error:
                self.current_prompt = self.error_instructions.format(rationale=rationale, error=error, csv_data=csv_data)

            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

        except ValueError as e:
            print(f"An error occurred during interaction: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_rml_codeblock(self):
        """
        Extract the RML code block from the LLM's response.

        Returns:
            str: The extracted RML code block.
        """
        return self.extract_text(self.answer, start_marker="```turtle", end_marker="```")
