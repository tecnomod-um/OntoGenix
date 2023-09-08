from abc import ABC
from typing import Optional
import re

from LLM_base.LlmBase import AbstractLlm
from tools import text2dict, compare_texts

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
        self.stable_plan = {}
        self.plan = None
        self.selected_instruction = None
        self.instructions = None # for future use in the GUI

    def interaction(self,
                    input_task: Optional[str] = None,
                    json_data: Optional[str] = None,
                    instructions: Optional[str] = None,
                    improvement_strategy: Optional[str] = None):
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
                self.current_prompt = self.first_instructions_prompt.format(input_task=input_task, json_data=json_data)
                # Get the response from the LLM_base
                response = self.get_api_response(self.current_prompt)
                self.update_memories(response)
            elif instructions:
                # Act as a subsequent interaction
                self.current_prompt = self.interaction_prompt.format(
                    input_plan=self.plan,
                    input_instructions=instructions,
                    short_term_memory=self.short_term_memory,
                    long_term_memory=self.long_term_memory
                )
                # Get the response from the LLM_base
                response = self.get_api_response(self.current_prompt)
                self.update_memories(response, first=False)
            elif improvement_strategy:
                self.current_prompt = self.interaction_prompt.format(
                    input_plan=self.plan,
                    improvement_strategy=improvement_strategy,
                    short_term_memory=self.short_term_memory
                )
                # Get the response from the LLM_base
                response = self.get_api_response(self.current_prompt)
                self.update_memories(response, first=False)
            else:
                raise ValueError("Insufficient arguments provided for interaction")

        except ValueError as e:
            print(f"An error occurred: {e}")
        finally:
            self.last_prompt = self.current_prompt

    def regenerate(self):
        # Reuse the last prompt
        response = self.get_api_response(self.last_prompt)

        # Check if the last prompt was for the first interaction or a subsequent one
        if self.instructions:
            # If it was a subsequent interaction, use the update_memories method for subsequent interactions
            self.update_memories(response, first=False)
        else:
            # If it was the first interaction, use the update_memories method for the first interaction
            self.update_memories(response, first=True)

        # Return the response from the model
        return response

    def update_memories(self, response: str, first: bool = True):
        try:
            print('update memories, first: ', first)
            self.save_response(response, self.dataset_path + '_general_plan.txt', mode='w')
            # extract the generated plan from the answer
            if first:
                self.short_term_memory = self.extract_text(response, "**Output Memory:**", "**Output Tasks:**").strip()
            else:
                self.short_term_memory = self.extract_text(response, "**Updated Memory:**", "**Output Tasks:**").strip()
            # extract the generated plan from the answer
            self.plan = self.extract_text(response, "**Output Tasks:**", "**Instructions:**").strip()
            self.update_plan()
            # extract the generated instructions from the answer
            self.instructions = self.extract_text(response, "**Instructions:**", "FINISH").strip()
        except ValueError as e:
            print(f"An error occurred: {e}")

    def update_plan(self):
        if self.stable_plan:
            old_instructions = "".join([key + ': ' + self.stable_plan[key] + '\n' for key in self.stable_plan.keys()])
        else:
            old_instructions = ""
        print(self.stable_plan)
        print(old_instructions)
        updated_instructions = compare_texts(old_instructions, self.plan)
        print(updated_instructions)
        positive_tasks = re.findall(r'\[\+\] (.+)', updated_instructions)
        print(positive_tasks)
        for task in positive_tasks:
            if 'task_' in task:
                new_task = text2dict(task)
                print('newtask', new_task)
                if self.stable_plan:
                    self.stable_plan.update(new_task)
                else:
                    for key, value in new_task.items():
                        print(key, value)
                        self.stable_plan[key] = value

        print(self.stable_plan)




