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
        self.first_instructions_prompt = self.load_string_from_file(metadata['first_instructions'])
        self.interaction_prompt = self.load_string_from_file(metadata['interaction'])
        self.dataset_path = metadata['dataset']

        # Initialize memories
        self.short_term_memory = None
        self.long_term_memory = None
        self.plan = None
        self.selected_instruction = None
        self.instructions = None # for future use in the GUI

    def interaction(self,
                    input_task: Optional[str] = None,
                    json_data: Optional[str] = None,
                    instructions: Optional[str] = None):
        """
        Perform the first interaction or a subsequent interaction with the LLM_base based on the arguments provided.

        Parameters:
        input_task (str): The input message. If this is provided, the method will act as first_interaction.
        json_data (str): The input data in JSON format. If this is provided, the method will act as first_interaction.
        instructions (str): The instructions for the interaction. If this is provided, the method will act as a subsequent interaction.

        Returns:
        str: The response from the LLM_base.
        """
        try:
            if input_task and json_data:
                # Act as first_interaction
                prompt = self.first_instructions_prompt.format(input_task=input_task, json_data=json_data)
            elif instructions:
                # Act as a subsequent interaction
                prompt = self.interaction_prompt.format(
                    input_plan=self.plan,
                    input_instructions=instructions,
                    short_term_memory=self.short_term_memory,
                    long_term_memory=self.long_term_memory
                )
            else:
                raise ValueError("Insufficient arguments provided for interaction")


            print('############## prompt #########################\n', prompt)
            # Get the response from the LLM_base
            response = self.get_api_response(prompt)
            self.update_memories(response)

        except ValueError as e:
            print(f"An error occurred: {e}")

    def update_memories(self, response: str):
        try:
            print('################### ANSWER ##############\n', response)
            # extract the generated plan from the answer
            self.short_term_memory = self.extract_text(response, "Updated Memory:", "Output Tasks:").strip()
            # extract the generated plan from the answer
            self.plan = self.extract_text(response, "BEGIN", "END")
            # extract the generated instructions from the answer
            self.instructions = self.extract_text(response, "START", "FINISH").strip()
            print('################### PLAN ##############\n', self.plan)

            self.save_response(self.plan, self.dataset_path + '_general_plan.txt', mode='a')

        except ValueError as e:
            print(f"An error occurred: {e}")


'''akjsdñflkjasdñflkjañsdflkj asdf
'''