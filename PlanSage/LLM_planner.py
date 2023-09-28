from abc import ABC
from typing import Optional

from LLM_base.LlmBase import AbstractLlm


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
        self.instructions_prompt = self.load_string_from_file(metadata['instructions'])
        self.dataset_path = metadata['dataset']

    def interaction(self,
                    input_task: Optional[str] = None,
                    json_data: Optional[str] = None):
        """
        Perform the first interaction or a subsequent interaction with the LLM_base based on the arguments provided.

        Parameters:
        input_task (str): The input message. If this is provided, the method will act as first_interaction.
        json_data (str): The input data in JSON format. If this is provided, the method will act as first_interaction.

        Returns:
        str: The response from the LLM_base.
        """
        try:
            if input_task and json_data:
                # Act as first_interaction
                self.current_prompt = self.instructions_prompt.format(input_task=input_task, json_data=json_data)
                # Get the response from the LLM_base
                self.get_api_response(self.current_prompt)
                # write the response in a txt file
                self.save_response(self.answer, self.dataset_path + '_rationale_and_tasks.txt', mode='w')
            else:
                raise ValueError("Insufficient arguments provided for interaction")

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def regenerate(self):
        try:
            # Reuse the last prompt
            self.get_api_response(self.last_prompt)
            # write the response in a txt file
            self.save_response(self.answer, self.dataset_path + '_rationale_and_tasks.txt', mode='w')

        except ValueError as e:
            print(f"An error occurred: {e}")




