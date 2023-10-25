from abc import ABC
from typing import Optional

from LLM_base.LlmBase import AbstractLlm
from enum import Enum

class OntologyState(Enum):
    DESCRIPTION = "DATA_DESCRIPTION"
    INIT_CONTEXT = "INITIAL_CONTEXT"

class LlmPlanner(AbstractLlm, ABC):
    """
    This class represents a language learning model (LLM_base) ontology. It extends the AbstractLlm class and provides
    methods for interacting with the model.

    TODO: the long_term_memory mechanism is not implemented.
    """

    def __init__(self, metadata: dict):
        """
        Initialize the LlmOntology object.

        Parameters:
        metadata (dict): A dictionary containing metadata for the LLM_base.
        """
        super().__init__(metadata)

        # initialize prompts
        self.data_description_prompt = self.load_string_from_file(metadata['data_description'])
        # self.instructions_prompt = self.load_string_from_file(metadata['instructions'])
        # initialize containers
        self._dataset_path = metadata['dataset']
        self.data_description = None
        # self.rationale = None

        # Getter for name
    @property
    def dataset_path(self):
        return self._dataset_path

    # Setter for name
    @dataset_path.setter
    def dataset_path(self, path):
        if not isinstance(path, str):
            raise ValueError("Name must be a string!")
        self._dataset_path = path

    async def interaction(self, input_task: Optional[str] = None,
                          json_data: Optional[str] = None,
                          data_description: Optional[str] = None,
                          state: OntologyState = None):
        """
        Perform the first interaction or a subsequent interaction with the LLM_base based on the arguments provided.

        Parameters:
        input_task (str): The input message.
        json_data (str): The input data in JSON format.
        data_description (str): The description of the JSON data.
        Yields:
        str: Chunks of the response from the LLM_base.
        """
        try:
            if state.value == OntologyState.DESCRIPTION.value:
                # Act as first_interaction
                self.current_prompt = self.data_description_prompt.format(input_task=input_task, json_data=json_data)
                # Get the response from the LLM_base
                async for chunk in self.get_async_api_response(self.current_prompt):
                    yield chunk
                # permanently store the generated data description answer
                self.data_description = self.answer

            # elif state.value == OntologyState.INIT_CONTEXT.value:
            #     # Act as first_interaction
            #     self.current_prompt = self.instructions_prompt.format(data_description=data_description)
            #     # Get the response from the LLM_base
            #     async for chunk in self.get_async_api_response(self.current_prompt):
            #         yield chunk
            #     # permanently store the generated rationale answer
            #     self.rationale = self.answer

            else:
                raise ValueError("Insufficient arguments provided for interaction")

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt




