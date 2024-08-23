from GUI.LLM_base.LlmBase import AbstractLlm
from typing import Optional
import os

class LlmOntology(AbstractLlm):
    """
    A class to manage ontology-related interactions with a language learning model.

    This class extends AbstractLlm and specializes in generating and managing interactions
    for ontology creation and entity improvement based on the provided data description.

    Attributes:
        ontology_instructions (str): Template for instructions related to ontology generation.
        entity_improvement (str): Template for instructions related to improving ontology entities.
        _dataset_path (str): Path to the dataset used in interactions.
    """

    def __init__(self, metadata: dict):
        """
        Initialize the LlmOntology object.

        Args:
            metadata (dict): Metadata for the LLM, including file paths and configurations.
        """
        super().__init__(metadata)
        self.ontology_instructions = self.load_string_from_file(metadata['ontology_instructions'])
        self.entity_improvement = self.load_string_from_file(metadata['entity_improvement'])
        self._dataset_path = metadata['dataset']

    @property
    def dataset_path(self) -> str:
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

        Args:
            path (str): The new path for the dataset.

        Raises:
            ValueError: If the provided path is not a string.
        """
        if not isinstance(path, str):
            raise ValueError("Path must be a string!")
        self._dataset_path = path

    async def interact(self,
                       json_data: Optional[str] = None,
                       data_description: Optional[str] = None,
                       task: Optional[str] = None,
                       entity: Optional[str] = None,
                       state: str = "ONTOLOGY"):
        """
        Perform an interaction with the LLM for ontology-related tasks.

        Based on the state, this method formats and sends the appropriate prompt to the LLM for interaction.

        Args:
            json_data (Optional[str]): JSON formatted data for the interaction.
            data_description (Optional[str]): Description of the data.
            task (Optional[str]): Instructions to improve the entity.
            entity (Optional[str]): The specific entity to be improved in the ontology.
            state (str): The current state of ontology interaction (e.g., "ONTOLOGY" or "ONTOLOGY_ENTITY").

        Yields:
            str: Chunks of the response from the LLM.

        Exceptions:
            ValueError: Catches and prints any ValueError that occurs during the interaction.
        """
        try:
            if state == "ONTOLOGY":
                self.current_prompt = self.ontology_instructions.format(
                    json_data=json_data,
                    data_description=data_description
                )
            elif state == "ONTOLOGY_ENTITY":
                self.current_prompt = self.entity_improvement.format(
                    task=task,
                    data_description=data_description,
                    entity=entity
                )

            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

        except ValueError as e:
            print(f"An error occurred during interaction: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def get_xml_codeblock(self) -> str:
        """
        Extract an XML code block from the LLM's response.

        Returns:
            str: The extracted XML code block from the LLM's response.
        """
        return self.extract_text(self.answer, start_marker="```xml", end_marker="```")
