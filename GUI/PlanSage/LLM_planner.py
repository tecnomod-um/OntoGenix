from abc import ABC
from typing import Optional

from GUI.LLM_base.LlmBase import AbstractLlm

class LlmPlanner(AbstractLlm, ABC):
    """
    A class representing a language learning model's ontology for planning.

    This class extends the AbstractLlm class and specializes in generating data descriptions
    and managing interactions with a language learning model. It stores and manages the data
    description prompts and the responses from the LLM.

    Attributes:
        data_description_prompt (str): The template for crafting data description prompts.
        data_description (Optional[str]): The last generated data description, stored after interactions.
        _dataset_path (str): The path to the dataset used in the LLM interactions.
    """

    def __init__(self, metadata: dict):
        """
        Initialize the LlmPlanner object.

        Parameters:
            metadata (dict): Metadata for the LLM, including file paths and configurations.
        """
        super().__init__(metadata)
        self.data_description_prompt = self.load_string_from_file(metadata['data_description'])
        self._dataset_path = metadata['dataset']
        self.data_description = None

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

        Parameters:
            path (str): The new path for the dataset.

        Raises:
            ValueError: If the provided path is not a string.
        """
        if not isinstance(path, str):
            raise ValueError("Path must be a string!")
        self._dataset_path = path

    async def interaction(self, input_task: Optional[str] = None, json_data: Optional[str] = None):
        """
        Perform an interaction with the LLM, generating a data description based on the provided task and data.

        Parameters:
            input_task (Optional[str]): The initial input task for generating the data description.
            json_data (Optional[str]): The input data in JSON format to be used in the data description.

        Yields:
            str: Chunks of the response from the LLM.

        Exceptions:
            ValueError: Catches and prints any ValueError that occurs during the interaction.
        """
        try:
            self.current_prompt = self.data_description_prompt.format(input_task=input_task, json_data=json_data)

            async for chunk in self.get_async_api_response(self.current_prompt):
                yield chunk

            self.data_description = self.answer

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt
