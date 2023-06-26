from abc import ABC
from typing import Tuple

from OntoGenix_v_1_1.LLM.LlmBase import AbstractLlm


class LlmPlanner(AbstractLlm, ABC):
    """
    This class represents a language learning model (LLM) ontology. It extends the AbstractLlm class and provides
    methods for interacting with the model.
    """

    def __init__(self, metadata: dict):
        """
        Initialize the LlmOntology object.

        Parameters:
        metadata (dict): A dictionary containing metadata for the LLM.
        """
        super().__init__(metadata)

        # Load the first instructions from a file
        self.first_instructions = self.load_string_from_file(metadata['first_instructions'])

        # Load the instructions from a file
        self.instructions = self.load_string_from_file(metadata['instructions'])

        # Initialize short-term memory for context management
        self.short_term_memory = None

        # Initialize long-term memory for context management
        self.long_term_memory = None

        # Initialize the plan container
        self.plan = None

        # Initialize the instruction storage
        self.instruction = None

    def first_interaction(self, input_task: str, json_data: str) -> Tuple[str, str]:
        """
        Perform the first interaction with the LLM.

        Parameters:
        input_task (str): The input message.
        json_data (str): The input data in JSON format.

        Returns:
        str: The response from the LLM.
        """
        try:
            # Format the first instructions with the input message and data
            prompt = self.first_instructions.format(input_task=input_task, json_data=json_data)

            # Get the response from the LLM
            response = self.get_api_response(prompt)
            plan = self.extract_text(response, "START", "END").strip()
            print('################### PLAN ##############\n', plan)

            return response, plan

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None

    def interaction(self, plan: str, instruction: str, short_t_mem: str, long_t_mem: str) -> str:
        """
        Perform an interaction with the LLM.

        Parameters:
        plan (str): The plan for the interaction.
        instruction (str): The instruction for the interaction.
        short_t_mem (str): The short-term memory for the interaction.
        long_t_mem (str): The long-tplanerm memory for the interaction.

        Returns:
        str: The response from the LLM.
        """
        try:
            # Set the plan, instruction, short-term memory, and long-term memory
            self.plan = plan
            self.instruction = instruction
            self.short_term_memory = short_t_mem
            self.long_term_memory = long_t_mem

            # Format the instructions with the plan, instruction, short-term memory, and long-term memory
            prompt = self.instructions.format(
                input_plan=self.plan,
                input_instruction=self.instruction,
                short_term_memory=self.short_term_memory,
                long_term_memory=self.long_term_memory
            )

            # Get the response from the LLM
            response = self.get_api_response(prompt)
            plan = self.extract_text(response, "START", "END").strip()
            print('################### PLAN ##############\n', plan)

            return response

        except ValueError as e:
            print(f"An error occurred while extracting text: {e}")
            return None
